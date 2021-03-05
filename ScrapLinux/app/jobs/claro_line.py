# -*- coding: utf-8 -*-
from app import app, db
from collections import Counter
from datetime import datetime, date
from io import BytesIO
from jobs.utils import get_driver, get_proxy
from models.osiptel import RRLL, TelephoneLine
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


def scrap_and_recognize(driver, rrll):
    driver.set_window_size(1400, 800)
    driver.get('https://aplicaciones.claro.com.pe/ClienteLineasWeb/')

    driver.find_element_by_xpath("//select[@id='iddoc']/option[text()='RUC']").click()
    driver.find_elements_by_id('numdoc')[0].send_keys(rrll.ruc)
    driver.find_element_by_xpath("//select[@id='iddoclegal']/option[text()='DNI']").click()
    driver.find_elements_by_id('numdoclegal')[0].send_keys(rrll.dni)

    solved = False
    result_void = False
    while not solved:
        captcha_image_selector = '#token'
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
                logger.info('\tCaptcha solved: {}'.format(captcha))
                driver.find_elements_by_id('captcha')[0].send_keys(captcha)
                driver.find_elements_by_class_name('btn-turquesa')[0].click()

                time.sleep(3)
                parent_div = driver.find_element_by_xpath('//div[contains(@class, "box-text-result")]')
                if parent_div is not None:
                    text_p = parent_div.find_element_by_xpath('//p').text.strip()
                    if text_p == 'El número de documento del Representante Legal no se encuentran asociado al número de RUC.' or text_p == 'No se encontraron resultados para tu búsqueda.':
                        solved = True
                        result_void = True
                        logger.info('\tCaptcha solved but no records found')
                    else:
                        solved = True
                        logger.info('\tScraping solved')
                else:
                    logger.info('\tIncorrect captcha')

    if result_void is True:
        records = []
    else:
        driver.find_element_by_id('showme').click()
        # Search for results
        logger.info('\tClick on Showme.')
        div = driver.find_element_by_xpath('//div[contains(@class, "body-table")]')
        trows = div.find_elements_by_xpath('//table/tbody/tr')
        logger.info('\tFinding <tr> on table')
        records = []
        for trow in trows:
            tds = trow.find_elements_by_tag_name('td')
            modality = tds[1].text
            telephone = tds[0].text
            records.append({
                'modality': modality,
                'telephone': telephone
            })

    return {
        'id': rrll.id,
        'ruc': rrll.ruc,
        'dni': rrll.dni,
        'records': records,
        'status': 1
    }


def scrap_claro_lines(rrll):
    max_retries = 3
    logger.info('\tStarting')
    logger.info('\tQuerying {}'.format(rrll.ruc))
    proxy_server = get_proxy(service='claro_line')
    if not proxy_server:
        logger.info('\tError: Out of proxies!')
        logger.info('\tFinished')
        return

    processed = False
    retries = 0
    while not processed:
        if retries == max_retries:
            logger.info('\tGiving up!')
            # Update rrll status record
            rrll.status = 3 # Error
            rrll.save()
            break
        try:
            logger.info('\tUsing proxy {}'.format(proxy_server))
            driver = get_driver(proxy_server)
            v_json = scrap_and_recognize(driver, rrll)
            if v_json['ruc'] != rrll.ruc and v_json['dni'] != rrll.dni:
                v_json['status'] = 2 # Invalid

            # Update rrll fields and create rrll records
            rrll.status = v_json['status']
            rrll.save()
            if v_json['records']:
                for record in v_json['records']:
                    TelephoneLine.create(
                        rrll=rrll,
                        modality=record['modality'],
                        telephone=record['telephone'],
                    )

            processed = True
            logger.info('\tProcessed')
        except Exception as e:
            logger.info('\tError: {}'.format(e))
            rrll.status = 3 # Error
            rrll.save()
            processed = True
        finally:
            try:
                driver.quit()
            except Exception:
                pass

    logger.info('\tFinished')
