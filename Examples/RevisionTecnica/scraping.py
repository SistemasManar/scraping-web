from bs4 import BeautifulSoup as soup
import functions.pillowExtractImage as PEI
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from random import seed
from random import randint

citv_url = "http://portal.mtc.gob.pe/reportedgtt/form/frmconsultaplacaitv.aspx"

driver = webdriver.Chrome()
driver.get(citv_url)
assert "SCC || Sistema de Consulta de CITV" in driver.title

while True:
    image_loaded = PEI.load_captcha(soup(driver.page_source, "html.parser"))
    print("Si hay match: " + image_loaded)
    element = driver.find_element_by_id("cboFiltroBusqueda")
    element.send_keys("1")
    element = driver.find_element_by_id("txtPlaca")
    element.send_keys("A5C315")
    element = driver.find_element_by_id("txtCaptcha")
    element.send_keys(image_loaded)
    element = driver.find_element_by_id("BtnBuscar")
    element.click()
    time.sleep(5)

    page_soup = soup(driver.page_source, "html.parser")

    if page_soup.find("div", {"style" : "text-align: center; padding-left: 30px; padding-right: 30px; display: none;"}) is None:
        print("No leyo bien la imagen.")
        seed(1)
        value = randint(3, 5)
        time.sleep(value)
        driver.refresh()
    else:
        containers = page_soup.findAll("div", {"id": "divDetalle"})
        container = containers[0]
        table_div = container.findAll("table", attrs={"class": "table"})

        table_data = []
        for table in table_div:
            table_gridHead = table.tbody.findAll("tr", attrs={"class": "gridHead"})
            table_gridItemGroup = table.tbody.findAll("tr", attrs={"class": "gridItemGroup"})
            t_headers = []
            for th in table_gridHead[0].findAll("th"):
                t_headers.append(th.text.replace('\n', ' ').strip())
            t_row = {}
            for td, th in zip(table_gridItemGroup[0].find_all("td"), t_headers):
                t_row[th] = td.text.replace('\n', '').strip()
            table_data.append(t_row)
        print(table_data)
        driver.quit()
        break
