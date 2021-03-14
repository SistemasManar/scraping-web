# -*- coding: utf-8 -*-
from app import app, db
from datetime import datetime, date
from io import BytesIO
from jobs.utils import get_driver, get_proxy
from models.doctor import Doctor, DoctorSpecialty
from PIL import Image
from rq.worker import logger
import os
import paramiko
import peewee
import requests


URL = 'https://200.48.13.39/cmp/php/detallexmedico.php?id={}'


def scrap_and_recognize(driver, doctor):
    driver.set_window_size(1200, 800)
    driver.get(URL.format(doctor.id))

    # Find the table for CMP, Name and Surname
    table1 = driver.find_element_by_id('simple-example-table1')
    table1_tr = table1.find_elements_by_tag_name('tr')[1]
    cmp_td, surname_td, name_td = table1_tr.find_elements_by_tag_name('td')
    cmp = cmp_td.text.strip()
    surname = surname_td.text.strip()
    name = name_td.text.strip()

    # Check for errors
    if 'Undefined variable' in name or 'Undefined variable' in surname:
        return {
            'cmp': None,
            'name': None,
            'surname': None,
            'state': None,
            'email': None,
            'region': None,
            'notes': None,
            'status': 1, # Processed
            'specialties': [],
        }

    # Find the tables for the doctor picture, state, email, region and notes
    # There's another nested table here
    table2 = driver.find_element_by_id('simple-example-table2')
    table2_state_tr, table2_image_tr, _, table2_email_region, table2_notes_tr = table2.find_elements_by_tag_name('tr')
    state_td = table2_state_tr.find_elements_by_tag_name('th')[0]
    state = state_td.text.strip()
    image_td = table2_image_tr.find_elements_by_tag_name('td')[0]
    image = image_td.find_element_by_tag_name('img').get_attribute('src')
    email_td, region_td = table2_email_region.find_elements_by_tag_name('td')
    email = email_td.text.strip()
    region = region_td.text.strip()
    notes_td = table2_notes_tr.find_elements_by_tag_name('td')[0]
    notes = notes_td.text.strip()

    # Upload image to file server
    filename = '{}.jpg'.format(doctor.id)
    current_path = os.path.abspath(os.path.dirname(__file__))
    local_path = os.path.join(current_path, 'files', filename)
    response = requests.get(image)
    memory_file = BytesIO(response.content)
    image_file = Image.open(memory_file)
    image_file.save(local_path)
    image_file.close()
    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join('/home/cesarbustios', '.ssh', 'known_hosts')))
    ssh.connect(app.config['FILES_SERVER'], username='root')
    sftp = ssh.open_sftp()
    folder = datetime.now().strftime('%d-%m-%Y_%H')
    remote_dir = os.path.join('/home/cesarbustios/files/', folder)
    try:
        sftp.chdir(remote_dir)
    except IOError:
        sftp.mkdir(remote_dir)
        sftp.chdir(remote_dir)
    sftp.put(local_path, filename)
    sftp.close()
    ssh.close()
    memory_file.close()
    os.remove(local_path)

    # Parse the specialties
    specialties = []
    table4 = driver.find_element_by_id('simple-example-table4')
    table4_trs = table4.find_elements_by_tag_name('tr')[1:]
    for tr in table4_trs:
        name_td, type_td, code_td, end_date_td = tr.find_elements_by_tag_name('td')
        specialty_name = name_td.text.strip()
        specialty_type = type_td.text.strip()
        specialty_code = code_td.text.strip()
        specialty_end_date_raw = end_date_td.text.strip()
        try:
            specialty_end_date = datetime.strptime(
                specialty_end_date_raw,
                '%d/%m/%Y'
            ).date()
        except Exception as e:
            specialty_end_date = None
        specialties.append({
            'name': specialty_name,
            'type': specialty_type,
            'code': specialty_code,
            'end_date': specialty_end_date,
        })

    return {
        'cmp': cmp,
        'name': name,
        'surname': surname,
        'state': state,
        'email': email,
        'region': region,
        'notes': notes,
        'image_path': os.path.join(folder, filename),
        'status': 1, # Processed
        'specialties': specialties,
    }



def scrap_cmp(doctor):
    max_retries = 3
    logger.info('\tStarting')
    logger.info('\tQuerying {}'.format(doctor.id))
    proxy_server = get_proxy(service='cmp')
    if not proxy_server:
        logger.info('\tError: Out of proxies!')
        logger.info('\tFinished')
        return

    processed = False
    retries = 0
    while not processed:
        if retries == max_retries:
            logger.info('\tGiving up!')
            # Update doctor status record
            doctor.status = 3 # Error
            doctor.save()
            break
        try:
            logger.info('\tUsing proxy {}'.format(proxy_server))
            driver = get_driver(proxy_server)
            record = scrap_and_recognize(driver, doctor)
            if record['cmp'] != doctor.id:
                record['status'] = 2 # Invalid

            # Update doctor fields and create specialties if applicable
            doctor.name = record['name']
            doctor.surname = record['surname']
            doctor.state = record['state']
            doctor.email = record['email']
            doctor.region = record['region']
            doctor.notes = record['notes']
            doctor.image_path = record['image_path']
            doctor.status = record['status']
            doctor.save()
            if record['specialties']:
                for specialty in record['specialties']:
                    DoctorSpecialty.create(
                        doctor=doctor,
                        name=specialty['name'],
                        type=specialty['type'],
                        code=specialty['code'],
                        end_date=specialty['end_date'],
                    )

            processed = True
            logger.info('\tProcessed')
        except Exception as e:
            logger.info('\tError: {}'.format(e))
            processed = True
        finally:
            try:
                driver.quit()
            except Exception:
                pass

    logger.info('\tFinished')
