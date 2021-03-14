from bs4 import BeautifulSoup as soup
import time
from selenium import webdriver

url = "https://ccplima.com.pe/colegiados/"
chromedriver = "/usr/local/bin/chromedriver"

driver = webdriver.Chrome(executable_path=chromedriver)
driver.get(url)
assert "CCPL - ONLINE" in driver.title
cont = 1

while i < 3:
    print("Reading.. c_cmp: " + conti)
    element = driver.find_element_by_id("caja_busqueda")
    element.clear()
    element.send_keys(cont)
    time.sleep(3)

    page_soup = soup(driver.page_source, "html.parser")
    container = page_soup.find("div", {"id": "datos"})

    print(container)

    table = len(container.find_all("table", recursive=False))

    print(table)
    '''
    table_div = containers.findAll("table", attrs={"class": "tabla_datos"})

    json_data_1 = {}
    for table in table_div:
        table_gridHead = table.thead.find("tr")
        table_gridItemGroup = table.tbody.find("tr")
        t_headers = []
        for th in table_gridHead.findAll("th"):
            t_headers.append(th.text.replace('\n', ' ').strip())
        for td, th in zip(table_gridItemGroup.findAll("td"), t_headers):
            json_data_1[th] = td.text.replace('\n', '').strip()
    '''
    
driver.quit()
