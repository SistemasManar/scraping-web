from bs4 import BeautifulSoup as soup
import time
from selenium import webdriver

#Scraping LIMA

url = "https://ccplima.com.pe/colegiados/"
chromedriver = "/usr/local/bin/chromedriver"

driver = webdriver.Chrome(executable_path=chromedriver)
driver.get(url)
assert "CCPL - ONLINE" in driver.title
ch_data = []
cont = 100

while cont < 37800:
    print("Reading.. c_cmp: {}".format(cont))
    element = driver.find_element_by_id("caja_busqueda")
    element.clear()
    element.send_keys(cont)
    time.sleep(2)

    page_soup = soup(driver.page_source, "html.parser")
    container = page_soup.find("div", {"id": "datos"})
    table_div = container.find_all("table", recursive=False)

    if len(table_div) == 1:
        print('Preparing..')
        json_data_1 = {}
        for table in table_div:
            table_gridHead = table.thead.find("tr")
            table_gridItemGroup = table.tbody.find("tr")
            t_headers = []
            for th in table_gridHead.findAll("td"):
                t_headers.append(th.text.replace('\n', ' ').strip())
            for td, th in zip(table_gridItemGroup.findAll("td"), t_headers):
                json_data_1[th] = td.text.replace('\n', '').strip()

        print('Adding to json..')
        ch_data.append(json_data_1)
        with open("data_scrp.json", "w") as text_file:
            text_file.write("{}".format(ch_data))

    else:
        print('No rows.')

    time.sleep(1)
    cont += 1

driver.quit()
