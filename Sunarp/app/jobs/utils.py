# -*- coding: utf-8 -*-
from app import app, db
from datetime import datetime, date
from models.proxy import Proxy
from selenium import webdriver
import os
import secrets


def get_proxy(service):
    query = Proxy.select().where(
        Proxy.service == service,
        Proxy.created == date.today()
    )
    used_proxies = [p.ip for p in query]
    proxies = app.config['PROXY_LIST']
    valid_proxies = list(filter(lambda p: p not in used_proxies, proxies))
    if valid_proxies:
        return secrets.choice(valid_proxies)
    return None


def get_driver(proxy_server):
    executable_path = os.path.join(app.config['JOBS_ROOT'], app.config['CHROME_DRIVER'])
    options = webdriver.ChromeOptions()
    if proxy_server and proxy_server != '127.0.0.1:80':
        options.add_argument('--proxy-server={}'.format(proxy_server))
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1200x600')
    driver = webdriver.Chrome(executable_path=executable_path, options=options)
    return driver
