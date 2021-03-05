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
import json


def scrap_and_recognize(driver, rrll):
    url_form = 'https://www.movistar.com.pe/movil/conoce-tus-numeros-moviles'
    driver.set_window_size(1400, 800)
    driver.get(url_form)

    select_ruc = driver.find_element_by_css_selector("#_consultmobilenumbers_WAR_consultmobilenumbersportlet_documentType")
    driver.execute_script("arguments[0].style.display = 'block';", select_ruc)
    driver.find_element_by_xpath("//select[@id='_consultmobilenumbers_WAR_consultmobilenumbersportlet_documentType']/option[text()=' RUC']").click()
    driver.find_elements_by_id('_consultmobilenumbers_WAR_consultmobilenumbersportlet_documentNumber')[0].send_keys(rrll.ruc)
    select_dni = driver.find_element_by_css_selector("#_consultmobilenumbers_WAR_consultmobilenumbersportlet_documentTypeRpstative")
    driver.execute_script("arguments[0].style.display = 'block';", select_dni)
    driver.find_element_by_xpath("//select[@id='_consultmobilenumbers_WAR_consultmobilenumbersportlet_documentTypeRpstative']/option[text()=' DNI']").click()
    driver.find_elements_by_id('_consultmobilenumbers_WAR_consultmobilenumbersportlet_documentNumberRpstative')[0].send_keys(rrll.dni)

    solved = False
    result_void = False
    while not solved:
        # Use 2Captha API to solve it
        in_params = {
            'method': 'userrecaptcha',
            'googlekey': '6LeJaRUUAAAAAA2iQkfdLPkK-vJ2mBqs8j_XA2-t',
            'key': app.config['CAPTCHA_KEY'],
            'pageurl': url_form,
            'json': 1
        }
        in_response = requests.post('https://2captcha.com/in.php', params=in_params)
        logger.info('\tSolving captcha')
        if in_response.ok:
            id_in = json.loads(in_response.text)["request"]
            logger.info('\tUsing id_in: {}'.format(id_in))
            res_params = {
                'key': app.config['CAPTCHA_KEY'],
                'action': 'get',
                'id': id_in,
                'json': 1
            }
            time.sleep(5)
            res_response = requests.get('https://2captcha.com/res.php', params=res_params)
            if res_response.ok:
                while json.loads(res_response.text)["request"] == 'CAPCHA_NOT_READY':
                    logger.info('\tCaptcha status: {}'.format(json.loads(res_response.text)["request"]))
                    time.sleep(2)
                    res_response = requests.get('https://2captcha.com/res.php', params={
                        'key': app.config['CAPTCHA_KEY'],
                        'action': 'get',
                        'id': id_in,
                        'json': 1
                    })
                resp_res = json.loads(res_response.text)["request"]

                # Fill the captcha input and submit
                logger.info('\tCaptcha solved: {}'.format(resp_res))
                txt_response = driver.find_element_by_css_selector("#g-recaptcha-response")
                driver.execute_script("arguments[0].innerHTML='{}';".format(resp_res), txt_response)
                time.sleep(1)
                driver.find_element_by_id('_consultmobilenumbers_WAR_consultmobilenumbersportlet_btnSubmit').click()
                
                time.sleep(3)
                parent_div = driver.find_element_by_xpath('//div[contains(@class, "content_result")]')
                if parent_div is not None:
                    if len(parent_div.find_elements_by_xpath('//center')) == 1:
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
        div_size = len(driver.find_elements_by_xpath('//div[contains(@class, "content_result")]/div'))
        logger.info('\tHow many divs "content_result": {}'.format(div_size))
        if div_size == 1:
            records = []
            scraping_with_pagination(driver, records)
            
        elif div_size == 2:
            records = []
            number_of_pages = int(driver.find_element_by_xpath('//div[@id = "tblData_paginate"]/span/a[last()]').text)
            logger.info('\tNro Pages: {}'.format(number_of_pages))
            
            for j in range(number_of_pages):
                scraping_with_pagination(driver, records)
                if j != range(number_of_pages):
                    logger.info('\tContinue scraping per page')
                    driver.find_element_by_xpath('//a[@id = "tblData_next"]').click()
                    time.sleep(1)
                
    return {
        'id': rrll.id,
        'ruc': rrll.ruc,
        'dni': rrll.dni,
        'records': records,
        'status': 1
    }
    

def scraping_with_pagination(driver, records):
    trows = driver.find_elements_by_xpath('//table[@id="tblData"]/tbody/tr')
    for trow in trows:
        tds = trow.find_elements_by_tag_name('td')
        modality = tds[0].text
        telephone = tds[1].text
        records.append({
            'modality': modality,
            'telephone': telephone
        })


def scrap_movistar_lines(rrll):
    max_retries = 3
    logger.info('\tStarting')
    logger.info('\tQuerying {}'.format(rrll.ruc))
    proxy_server = get_proxy(service='movistar_line')
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
