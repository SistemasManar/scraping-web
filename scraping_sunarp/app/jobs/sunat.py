from app import app, db

from datetime import datetime, date

from jobs.utils import get_driver, get_proxy

from models.proxy import Proxy

from models.sunat import RUC

#from PIL import Image, ImageFilter

from rq.worker import logger

from selenium.common.exceptions import JavascriptException, NoSuchElementException

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver

import requests
import time
 

def scrap_and_recognize(driver,ruc):
        
        print("starting")
        url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp'
        #url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias'

        driver.get(url)

        print(driver.get(url))
        time.sleep(5)
        logger.info(driver.title)
        containers_text = []
        element = driver.find_element_by_id("txtRuc").send_keys(ruc.id)
       # element = driver.find_element_by_xpath('//*[@id="txtRuc"]').send_keys(ruc.id)
        element = driver.find_element_by_id("btnAceptar")
        #print(records)
        element.click()
        time.sleep(2)
        divs_containers=0
        divs_containers = driver.find_elements_by_class_name('list-group-item')
        for div_in in divs_containers:   
           containers_text.append({           
              div_in.text
           })        
        len_containers = len(divs_containers)
        print("Containers text" + len_containers)
        if(len_containers==18 or 19):
            f=0
        if(len_containers >= 20):
               f=1
        if(len_containers == 0):
           logger.info("\t page error")
           return {
                  'id' : ruc.id,     
                  'status':3, #error   
              }

        records = []
        ruc_full_name = region = list(containers_text[f])[0].replace('\n', '').split('-')
        ruc_number = ruc_full_name[0].split(':')[1].replace(' ','')
        ruc_name = (ruc_full_name[1]).strip()       
        f=f+1
        contribuyente = list(containers_text[f])[0].split("\n")
        contribuyente = contribuyente[1]
        #print(contribuyente)
        f=f+1
        try:
           tipo_docu = list(containers_text[f])[0].split("\n")         
           if tipo_docu[0]=='Tipo de Documento:':        
              tipo_docu = list(containers_text[f])[0].split("\n")
              tipo_docu = tipo_docu[1]
              f=f+1
           else:
              tipo_docu = '-'
              f=f          
        except:
            print('error')

        nombreC = list(containers_text[f])[0].split("\n")
        nombreC = nombreC[1]
        f=f+1
        fechaInscripcion = list(containers_text[f])[0].split("\n")     
        fechaInicio = fechaInscripcion[3]
        fechaInscripcion = fechaInscripcion[1]
        f=f+1
        estadoC = list(containers_text[f])[0].split("\n")
        estadoC = estadoC[1]
        f=f+1
        condicionC = list(containers_text[f])[0].split("\n")
        condicionC = condicionC[1]
        f=f+1
        domicilio = list(containers_text[f])[0].split("\n")
        domicilio = domicilio[1]
        if(domicilio == '-'):
           domicilio=domicilio
           region='-'
           distrito='-'
        else:
           domicilio = region = list(containers_text[f])[0].replace('\n', '').split('-')[0].split(':')[1]
           region = list(containers_text[f])[0].replace('\n', '').split('-')[1].replace(' ', '')
           distrito = list(containers_text[f])[0].replace('\n', '').split('-')[2].replace(' ', '')
        f=f+1     
        sistemaEmisionC = list(containers_text[f])[0].split("\n")
        actividadComercio = sistemaEmisionC[3]
        sistemaEmisionC = sistemaEmisionC[1]      
        f=f+1      
        sistemaContabilidad = list(containers_text[f])[0].split("\n")
        sistemaContabilidad = sistemaContabilidad[1]
        f=f+1
        actividadEco = list(containers_text[f])[0].split("\n")
        actividadEcon = []
        for actividad in actividadEco[1:]:
         actividadEcon.append(actividad)
        actividadEcon=''.join(str(e) for e in actividadEcon).replace("[", "").replace("]", "")
        f=f+1
        comprobantesPago = list(containers_text[f])[0].split("\n")
        comprobantesP = []
        for comprobantes in comprobantesPago[1:]:
         comprobantesP.append(comprobantes)
        comprobantesP=''.join(str(e) for e in comprobantesP).replace("[", "").replace("]", "")      
        f=f+1
        sistemaEmisionE = list(containers_text[f])[0].split("\n")
        sistemaEmisionE  = sistemaEmisionE[1]
        f=f+1
        emisorElec = list(containers_text[f])[0].split("\n")
        emisorElec = emisorElec[1]
        f=f+1
        comprobantesE = list(containers_text[f])[0].split("\n")
        comprobantesE = comprobantesE[1]
        f=f+1
        afiliados = list(containers_text[f])[0].split("\n")
        afiliados = afiliados[1]
        f=f+1
        padrones = list(containers_text[f])[0].split("\n")
        padrones = padrones[1]
        element = driver.find_element_by_class_name('btnInfNumTra')
        element.click()
        time.sleep(2)
        #Table trabajadores
        # get number of Rows
        noOfRows = len(driver.find_elements_by_xpath("//tr"))
        #print(noOfRows)
        # get number of Columns
        noOfColumns = len(driver.find_elements_by_xpath("//tr[2]/td")) + 1
        allData = []
        for i in range(1,noOfRows):
           ro=[]
           for j in range(1,noOfColumns):
              ro.append(driver.find_element_by_xpath("//tr["+str(i)+"]/td["+str(j)+"]").text)
           allData.append(ro)
        #str1 = ''.join(allData)         
        allData=''.join(str(e) for e in allData).replace('[', '').replace(']', '|').replace("'", "").strip()
        if(allData==''):
           allData='-'
           ##print(type(allData)

        element = driver.find_element_by_class_name('btn-danger')
        element.click()

        time.sleep(2)

        element = driver.find_element_by_class_name('btnInfRepLeg')
        element.click()

        time.sleep(10)
        #Table representantes Legales
        # get number of Rows
        noOfRows2 = len(driver.find_elements_by_xpath("/html/body/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr"))+1
        #print(noOfRows2)
        # get number of Columns
        noOfColumns2 = len(driver.find_elements_by_xpath("/html/body/div/div[2]/div[2]/div[2]/div/div/table/thead/tr/th"))+1
        #print(noOfColumns2)
        allDataLe = []
        for i in range(1,noOfRows2):
           ro2 = []
           for j in range(1,noOfColumns2):              
               ro2.append(driver.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr["+str(i)+"]/td["+str(j)+"]").text)
           try:
              allDataLe.append(ro2)
           except ErrorInResponseException as e:
              print(e)
              

        allDataLe=''.join(str(e) for e in allDataLe).replace('[', '').replace(']', '|').replace("'", "").strip()

         
        time.sleep(2)

        return{
            'id' : ruc.id,
            'ruc_number':ruc_number ,
            'ruc_name':ruc_name,
            'contribuyente': contribuyente ,
            'tipo_docu':tipo_docu,
            'nombreC' : nombreC ,
            'fechaInicio':fechaInicio,
            'fechaInscripcion':fechaInscripcion,
            'estadoC':estadoC,
            'condicionC' : condicionC ,
            'actividadComercio':actividadComercio,
            'domicilio':domicilio,
            'region':region,
            'distrito':distrito,
            'sistemaEmisionC':sistemaEmisionC,
            'sistemaContabilidad':sistemaContabilidad,
            'actividadEco' : actividadEcon ,
            'comprobantesPago':comprobantesP,
            'emisorElec':emisorElec ,
            'comprobantesE':comprobantesE,
            'sistemaEmisionE':sistemaEmisionE,
            'afiliados':afiliados,
            'padrones':padrones ,
            'cantidadT' : allData ,
            'representantesLe' : allDataLe ,
            'status':1, #Processed         
        }  

            

def scrap_ruc_number (ruc):

   max_retries = 3
   logger.info('\tStarting')
   logger.info('\tQuerying {}'.format(ruc.id))
   proxy_server = get_proxy(service='sunat')

   if not proxy_server:
      logger.info('\tError: Out of proxies!')
      logger.info('\tFinished')
      return   

   processed = False

   retries = 0   

   while not processed:      

      if retries == max_retries:

         #print("\t Giving up!")

         logger.info('\tGiving up!')

         # Update ruc status record

         ruc.status = 3 #error

         ruc.save()

         break

      try:

         logger.info('\tUsing proxy {}'.format(proxy_server))
         driver = get_driver(proxy_server)
         print(driver)
         record = scrap_and_recognize(driver, ruc)
         print(record)
         

         if record['ruc_number'] != ruc.id :
            record['status'] = 2 #Invalid

         if record['status'] == 3 :
            print("PAGE ERROR")
            processed = True
         else:         

            # Update ruc fields 
            ruc.ruc_number = record['ruc_number']         
            ruc.ruc_name = record['ruc_name']
            ruc.tipo_contribuyente = record['contribuyente']
            ruc.tipo_docu = record['tipo_docu']
            ruc.nombre_comercial = record['nombreC']
            ruc.fecha_inic = record['fechaInicio']
            ruc.fecha_ins = record['fechaInscripcion']
            ruc.estado_contribuyente = record['estadoC']
            ruc.condicion_contribuyente = record['condicionC']
            ruc.domicilio = record['domicilio']
            ruc.region = record['region']
            ruc.distrito = record['distrito']
            ruc.sistema_emision_c= record['sistemaEmisionC']
            ruc.actividad_comercio = record['actividadComercio']
            ruc.sistema_contabilidad = record['sistemaContabilidad']
            ruc.actividad_economica = record['actividadEco']
            ruc.comprobante_pago = record['comprobantesPago']
            ruc.sistema_emision_e = record['sistemaEmisionE']
            ruc.emisor_electronico = record['emisorElec']
            ruc.comprobante_electronico = record['comprobantesE']     
            ruc.afiliado_ple = record['afiliados']
            ruc.padrones = record['padrones']
            ruc.owners = record['cantidadT']
            ruc.legalRe = record['representantesLe']
            ruc.status = record['status']
            ruc.save()
   
                      
   
                       
   
   
            processed = True
   
            #print("Processed")
   
            logger.info('\tProcessed')
   
      except NoSuchElementException as e:

         #print("\t Error: scraping problem")

         logger.info('\tError: Scraping problem')
         logger.info(e)
         ruc.status = 3 # Error

         ruc.save()

         processed = True         

         


      finally:

         if ruc.status == 3 :
            driver.quit()
         
         else:

            time.sleep(120)

         driver.quit()

logger.info('\tFinished')

#print(scrap_ruc(key))









      






   
        











