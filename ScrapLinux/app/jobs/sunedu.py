# -*- coding: utf-8 -*-
from app import app, db
from collections import Counter
from datetime import datetime, date
from io import BytesIO
from jobs.utils import get_driver, get_proxy
from models.graduate import Graduate, GraduateRecord
from models.proxy import Proxy
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from rq.worker import logger
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from subprocess import check_output
import os
import peewee
import requests
import time


def scrap_and_recognize(driver, graduate):
    driver.set_window_size(1400, 800)
    driver.get('https://enlinea.sunedu.gob.pe/')

    # Link to vehicle consulting
    driver.find_element_by_xpath('//div[contains(@class, "img_publica")]').click()

    modal_selector = '#modalConstancia'
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, modal_selector)))
    modal = driver.find_element_by_css_selector(modal_selector)
    modal.click()
    modal.find_elements_by_id('doc')[0].send_keys(graduate.id)

    ocr = ''
    solved = False
    first = True
    while not solved:
        captcha_image_selector = '#consultaForm #captchaImg img'
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, captcha_image_selector)))
        time.sleep(2)
        captcha_image = driver.find_element_by_css_selector(captcha_image_selector)
        body = captcha_image.screenshot_as_base64

        # Use 2Captha API to solve it
        in_params = {
            'method': 'base64',
            'key': app.config['CAPTCHA_KEY'],
            'body': body,
            'regsense': 1,
            'numeric': 4,
            'min_len': 5,
            'max_len': 5
        }
        in_response = requests.post('https://2captcha.com/in.php', params=in_params)
        logger.info('\tSolving captcha')
        if in_response.ok:
            captcha_id = in_response.text.split('|')[-1]
            res_params = {
                'key': app.config['CAPTCHA_KEY'],
                'action': 'get',
                'id': captcha_id
            }
            time.sleep(5)
            res_response = requests.get('https://2captcha.com/res.php', params=res_params)
            if res_response.ok:
                while res_response.text == 'CAPCHA_NOT_READY':
                    logger.info('\tCaptcha status: {}'.format(res_response.text))
                    time.sleep(2)
                    res_response = requests.get('https://2captcha.com/res.php', params={
                        'key': app.config['CAPTCHA_KEY'],
                        'action': 'get',
                        'id': captcha_id
                    })
                captcha = res_response.text.split('|')[-1]

                # Fill the captcha input and submit
                modal.find_elements_by_id('captcha')[0].send_keys(captcha)
                modal.find_elements_by_id('buscar')[0].click()
                time.sleep(2)

                error_body = modal.find_element_by_id('frmError_Body')
                if error_body.is_displayed():
                    error_message = error_body.text.strip()
                    if error_message == 'No se encontraron resultados.':
                        solved = True
                        logger.info('\tCaptcha solved: {}'.format(captcha))
                        logger.info('\tNo records found'.format(captcha))
                    else:
                        logger.info('\tIncorrect captcha: {}'.format(captcha))
                    modal.find_element_by_xpath('//button[@id = "closeModalError"]/span').click()
                else:
                    solved = True
                    logger.info('\tCaptcha solved: {}'.format(captcha))

    # Search for results
    trows = modal.find_elements_by_xpath('//tbody[@id = "finalData"]/tr')
    records = []
    for trow in trows[:10]: # Limiting to 10 records
        tds = trow.find_elements_by_tag_name('td')
        name = tds[0].text
        grade = tds[1].text
        institution = tds[2].text
        records.append({
            'name': name,
            'grade': grade,
            'institution': institution,
        })

    return {
        'id': graduate.id,
        'records': records,
        'status': 1, # Processed
    }


def scrap_document_number(graduate):
    max_retries = 3
    logger.info('\tStarting')
    logger.info('\tQuerying {}'.format(graduate.id))
    proxy_server = get_proxy(service='sunedu')
    if not proxy_server:
        logger.info('\tError: Out of proxies!')
        logger.info('\tFinished')
        return

    processed = False
    retries = 0
    while not processed:
        if retries == max_retries:
            logger.info('\tGiving up!')
            # Update graduate status record
            graduate.status = 3 # Error
            graduate.save()
            break
        try:
            logger.info('\tUsing proxy {}'.format(proxy_server))
            driver = get_driver(proxy_server)
            record = scrap_and_recognize(driver, graduate)
            if record['id'] != graduate.id:
                record['status'] = 2 # Invalid

            # Update graduate fields and create graduate records
            graduate.status = record['status']
            graduate.save()
            if record['records']:
                for record in record['records']:
                    GraduateRecord.create(
                        graduate=graduate,
                        name=record['name'],
                        grade=record['grade'],
                        institution=record['institution'],
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
