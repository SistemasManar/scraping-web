# -*- coding: utf-8 -*-
from app import app, db
from datetime import datetime, date
from jobs.utils import get_driver, get_proxy
from models.proxy import Proxy
from models.vehicle import Vehicle
from PIL import Image, ImageFilter
from rq.worker import logger
from selenium.common.exceptions import JavascriptException, NoSuchElementException
import base64
import io
import os
import paramiko
import peewee
import pytesseract
import requests


def remove_transparency(im, bg_colour=(255, 255, 255)):
    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg
    else:
        return im


def scrap_and_recognize(driver, vehicle):
    driver.get('https://www.sunarp.gob.pe/seccion/servicios/detalles/0/c3.html')

    # Link to vehicle consulting
    driver.find_element_by_xpath('//div[contains(@class, "jcrm-botondetalle")]/a').click()

    # Workaround: remove the ID of the element holding captcha image
    driver.execute_script('document.getElementById("ctl00_MainContent_captch_cv").setAttribute("id", "");')

    # Fill plate number
    plate_input = driver.find_element_by_xpath('//input[contains(@id, "MainContent_txtNoPlaca")]')
    plate_input.send_keys(vehicle.id)

    # Submit plate search
    driver.find_element_by_xpath('//input[contains(@id, "MainContent_btnSend")]').click()

    # Get image and save from base64
    state_element = driver.find_element_by_xpath('//input[contains(@id, "__VIEWSTATE")]')
    image_element = driver.find_element_by_xpath('//img[contains(@id, "MainContent_imgPlateCar")]')
    memory_file = io.BytesIO(base64.b64decode(image_element.get_attribute('src').split(',')[1]))
    filename = '{}.png'.format(vehicle.id)
    current_path = os.path.abspath(os.path.dirname(__file__))
    local_path = os.path.join(current_path, 'files', filename)

    # Open an enhance the image
    image_file = Image.open(memory_file)
    image_file.save(local_path)
    pixels = image_file.load()
    for i in range(image_file.size[0]): # for every pixel:
        for j in range(image_file.size[1]):
            pxs = pixels[i, j]
            if pxs[0] > 40:
                pixels[i, j] =  (0, 0, 0, 0)
    image_file = (image_file
        .filter(ImageFilter.SMOOTH)
        .filter(ImageFilter.DETAIL)
    )
    image_file = remove_transparency(image_file)
    width, height = image_file.size
    image_file = image_file.resize((int(width*2.5), int(height*1.5)), Image.ANTIALIAS)

    # Use Tesseract OCR
    ocr = pytesseract.image_to_string(image_file, lang='spa', config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ., -psm 6')
    ocr_text = list(filter(lambda row: row, ocr.split('\n')))

    # Upload image to file server
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

    # Some logic for trying to enhance OCR. "O" and "I" are not valid letters
    # for VINs
    serial_number = ocr_text[1].replace(' ', '').strip().replace('I', '1').replace('O', '0')

    return {
        'plate_number': vehicle.id,
        'serial_number': serial_number,
        'vin_number': serial_number,
        'engine_number': ocr_text[3].replace(' ', '').strip(),
        'color': ocr_text[4].strip(),
        'make': ocr_text[5].strip(),
        'model': ocr_text[6].strip(),
        'valid_plate_number': ocr_text[7].replace(' ', '').strip(),
        'previous_plate_number': ocr_text[8].replace(' ', '').strip(),
        'state': ocr_text[9].replace('EN CIRCULAC(ON', 'EN CIRCULACION').strip(),
        'notes': ocr_text[10].replace('N INGU NA', 'NINGUNA').strip(),
        'branch': ocr_text[11].replace('UMA', 'LIMA').strip(),
        'owners': '|'.join(ocr_text[12:]).strip(),
        'image_path': os.path.join(folder, filename),
        'status': 1, # Processed
    }


def scrap_plate_number(vehicle):
    max_retries = 3
    logger.info('\tStarting')
    logger.info('\tQuerying {}'.format(vehicle.id))
    proxy_server = get_proxy(service='sunarp')
    if not proxy_server:
        logger.info('\tError: Out of proxies!')
        logger.info('\tFinished')
        return

    processed = False
    retries = 0
    while not processed:
        if retries == max_retries:
            logger.info('\tGiving up!')
            # Update vechicle status record
            vehicle.status = 3 # Error
            vehicle.save()
            break
        try:
            logger.info('\tUsing proxy {}'.format(proxy_server))
            driver = get_driver(proxy_server)
            record = scrap_and_recognize(driver, vehicle)
            if record['plate_number'] != vehicle.id:
                record['status'] = 2 # Invalid

            # Update vehicle fields
            vehicle.plate_number = record['plate_number']
            vehicle.serial_number = record['serial_number']
            vehicle.vin_number = record['vin_number']
            vehicle.engine_number = record['engine_number']
            vehicle.color = record['color']
            vehicle.make = record['make']
            vehicle.model = record['model']
            vehicle.valid_plate_number = record['valid_plate_number']
            vehicle.previous_plate_number = record['previous_plate_number']
            vehicle.state = record['state']
            vehicle.notes = record['notes']
            vehicle.branch = record['branch']
            vehicle.owners = record['owners']
            vehicle.image_path = record['image_path']
            vehicle.status = record['status']
            vehicle.save()

            processed = True
            logger.info('\tProcessed')
        except NoSuchElementException:
            logger.info('\tError: Element not found')
            try:
                label = driver.find_element_by_xpath('//span[contains(@id, "MainContent_lblWarning")]')
                if 'número máximo' in label.text:
                    logger.info('\tError: Max queries reached for {}'.format(proxy_server))
                    # Save this invalid proxy in table and ask for another one
                    Proxy.create(service='sunarp', ip=proxy_server)
                    proxy_server = get_proxy(service='sunarp')
                    if not proxy_server:
                        logger.info('\tError: Out of proxies!')
                        processed = True
                    else:
                        retries += 1
                        logger.info('\tRetrying...')
            except NoSuchElementException:
                logger.info('\tError: Scraping problem')
                vehicle.status = 3 # Error
                vehicle.save()
                processed = True
            else:
                retries += 1
                logger.info('\tRetrying...')
        except JavascriptException:
            logger.info('\tError: Javascript')
            logger.info('\tRetrying...')
            retries += 1
        except AttributeError:
            # Probably something wrong with the license image
            logger.info('\tError: Invalid image')
            logger.info('\tRetrying...')
            retries += 1
        finally:
            try:
                driver.quit()
            except Exception:
                pass

    logger.info('\tFinished')
