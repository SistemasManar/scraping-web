from bs4 import BeautifulSoup as soup
import time
from selenium import webdriver
import ConexionBD.connection as conn_st

citv_url = "http://200.37.231.66/pegasoweb/publico/"

driver = webdriver.Chrome()
driver.get(citv_url)
assert "Colegio de Enfermeros del Perú" in driver.title
i = 879;

while i < 1000:
    print("Reading.. c_cmp: " + str(i).zfill(6))
    element = driver.find_element_by_id("c_cmp")
    element.clear()
    element.send_keys(str(i).zfill(6))
    element = driver.find_element_by_id("nombre")
    element.clear()
    element.send_keys("")
    element = driver.find_element_by_xpath("//button[@type='submit']")
    element.click()
    time.sleep(4)

    page_soup = soup(driver.page_source, "html.parser")
    containers = page_soup.find("div", {"id": "divListarRegistro"})
    table_div = containers.findAll("table", attrs={"class": "table"})

    json_data_1 = {}
    for table in table_div:
        table_gridHead = table.thead.find("tr")
        table_gridItemGroup = table.tbody.find("tr")
        t_headers = []
        for th in table_gridHead.findAll("th"):
            t_headers.append(th.text.replace('\n', ' ').strip())
        for td, th in zip(table_gridItemGroup.findAll("td"), t_headers):
            json_data_1[th] = td.text.replace('\n', '').strip()

    print(json_data_1['#'])
    if json_data_1['#'] == "Resultado 0":
        i += 1;
        continue
        time.sleep(4)
    else:
        element = driver.find_element_by_xpath("//a[@title='Nueva Consulta']")
        element.click()
        time.sleep(5)

        page_soup_det = soup(driver.page_source, "html.parser")
        containers_det = page_soup_det.findAll("div", {"class": "modal-body"})
        container_det = containers_det[0]
        table_colegiado = container_det.findAll("table", attrs={"class": "table-condensed"})
        table_consejo = container_det.findAll("table", attrs={"class": "table table-hover"})

        json_data_2 = {}
        for table_det_2 in table_colegiado:
            t_headers = []
            tb_tr2 = table_det_2.tbody.findAll("tr")
            for tr in tb_tr2:
                t_headers.append(tr.td.text.replace('\n', ' ').strip())
            for tr, th in zip(tb_tr2, t_headers):
                for td in tr.findAll("td")[2:]:
                    if len(td) == 1:
                        json_data_2[th] = td.text.replace('\n', '').strip()
                    else:
                        json_data_2["Imagen"] = td.img['src'].replace('..', 'http://200.37.231.66/pegasoweb')

        json_data_3 = {}
        for table_det_3 in table_consejo:
            table_Head = table_det_3.thead.find("tr")
            table_ItemGroup = table_det_3.tbody.find("tr")
            t_headers = []
            for th in table_Head.findAll("th")[1:]:
                t_headers.append(th.text.replace('\n', ' ').strip())
            for td, th in zip(table_ItemGroup.findAll("th")[1:], t_headers):
                json_data_3[th] = td.text.replace('\n', '').strip()

        conn_st.insert_t_cep(json_data_1['CEP'],json_data_1['Nombres'],json_data_1['CR Aportación'],json_data_1['Estado'])
        time.sleep(3)
        conn_st.insert_t_detalle_cep(json_data_2['CEP'], json_data_2['Apellido paterno'], json_data_2['Apellido materno'],
                                     json_data_2['Primer nombre'], json_data_2['Segundo nombre'], json_data_2['Condición'],
                                     json_data_2['Consejo Regional aporta'], json_data_3['Dirección'], json_data_3['Telefono'],
                                     json_data_3['Correo'], json_data_2['Imagen'])

        i += 1;
        element = driver.find_element_by_xpath("//button[@data-dismiss='modal']")
        element.click()
        time.sleep(4)

conn_st.close_conn()
driver.quit()
