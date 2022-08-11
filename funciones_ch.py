from csv import excel
import locale
from matplotlib import dates
from matplotlib.pyplot import bar_label
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from numpy import NaN
import numpy as np
import time
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from selenium.webdriver.support.ui import Select

def browserOptions(driverpath):
    path = os.getcwd()
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_experimental_option('prefs', {
    "download.default_directory": path
    })
    driver_path = driverpath
    driver = webdriver.Chrome(driver_path, options = options) 
    return driver

def getDownLoadedFileName(waitTime, driver):
    driver.execute_script("window.open()")
    # switch to new tab
    driver.switch_to.window(driver.window_handles[-1])
    # navigate to chrome downloads
    driver.get('chrome://downloads')
    # define the endTime
    endTime = time.time()+waitTime
    # return the file name once the download is completed
    return driver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")

def isEmpty(variable):
    if(variable == ''):
        variable = float(0)
    else:
        variable = float(variable)
    
    return variable

def dataCleaning(df):
    df = df.set_index('Fecha')
    df.dropna() 
    df = df.sort_index()

    return df

def reservasChina(driver):
     # Inicializar el navegador
    driver.get('https://www.safe.gov.cn/en/ForexReserves/index.html')

    forex_reserves = driver.find_elements_by_xpath('/html/body/div[3]/div/div[2]/div[3]/div[2]/ul/li')

    i = 1
    dates_list = []
    values_list = []

    for element in forex_reserves:
        element = element.text.split('\n')
        if('Official Reserve Assets'in element[0]):
            WebDriverWait(driver, 5)\
                .until(EC.element_to_be_clickable((By.XPATH, 
                '/html/body/div[3]/div/div[2]/div[3]/div[2]/ul/li['+str(i)+']/dt/a')))\
                    .click()       

            driver.switch_to.window(driver.window_handles[-1])                

            if('2019' in element[0]):

                dates = driver.find_elements_by_xpath('/html/body/div[3]/div/div[1]/div[3]/div[4]/table/tbody/tr[3]/td')
                values = driver.find_elements_by_xpath('/html/body/div[3]/div/div[1]/div[3]/div[4]/table/tbody/tr[6]/td')
            
            elif('2017' in element[0]):
                for p in range(1,6,2):
                    excel_url = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div[3]/div[4]/div/div[2]/p['+ str(p) +']/a').get_attribute('href')

                    archivo_excel = pd.ExcelFile(excel_url)

                    if(p == 1):
                        df = archivo_excel.parse('Sheet1', skiprows=3)
                        data = df.iloc[3]
                    elif(p == 3):
                        df = archivo_excel.parse('Sheet1', skiprows=1)
                        data = df.iloc[1]
                    elif(p==5):
                        df = archivo_excel.parse('Sheet1', skiprows=2)
                        data = df.iloc[1]
                    
                    data2 = data.reset_index()

                    for item in data2.iloc[:,0]:
                        if ('Unnamed' in str(item)):
                            data = data.drop(item)
                    
                    data = data.reset_index()
                    data = data.drop(0)

                    for date in data['index']:
                        date = datetime.strptime(str(date), '%Y.%m')
                        dates_list.append(date)

                    if(p == 1):
                        values_list.extend(data[3])  
                    elif(p == 3 or p == 5):
                        values_list.extend(data[1])
                    
                    print('-------SE EXTRAJO LA INFO EXCEL ' + str(p))                    
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])
                continue
            else:
                WebDriverWait(driver, 5)\
                    .until(EC.element_to_be_clickable((By.XPATH, 
                    '/html/body/div[3]/div/div[1]/div[3]/div[4]/div/div/div[2]/p/a')))\
                        .click() 

                if('2018' in element[0]):
                    driver.switch_to.window(driver.window_handles[-1])
            
                dates = driver.find_elements_by_xpath('/html/body/div[1]/table/tbody/tr[3]/td')
                values = driver.find_elements_by_xpath('/html/body/div[1]/table/tbody/tr[6]/td')       
           
            index_to_delete = list(range(0, 24, 2))

            values.pop(-1)
            dates.pop(0)

            for idx in sorted(index_to_delete, reverse = True):
                del values[idx]

            values_text = []
            for value in values:
                value = value.text
                if(value == ''):
                    value = NaN
                values_text.append(value)

            dates_text = []
            for date in dates:
                date = date.text
                date = datetime.strptime(date, '%Y.%m')
                dates_text.append(date)           


            dates_list.extend(dates_text)
            values_list.extend(values_text)

            driver.close()

            if('2018' in element[0]):
                driver.switch_to.window(driver.window_handles[-1])
                driver.close()

            print('------------SE EXTRAJO-----'+ element[0])

        elif('Exchange Reserves' in element[0]):

            WebDriverWait(driver, 5)\
                .until(EC.element_to_be_clickable((By.XPATH, 
                '/html/body/div[3]/div/div[2]/div[3]/div[2]/ul/li[15]/dt/a')))\
                    .click() 

            time.sleep(5)
            
            driver.switch_to.window(driver.window_handles[-1])

            excel_url = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div[3]/div[4]/p[4]/a').get_attribute('href')
            archivo_excel = pd.ExcelFile(excel_url)
            df = archivo_excel.parse('sheet1', skiprows=4)

            for date in df['Date']:
                date = datetime.strptime(str(date), '%B %Y')
                dates_list.append(date)

            values_list.extend(df['Amount'])

            driver.close()

            print('----------------------SE EXTRAJO LA INFO ANTES DEL 2015-----------')
        
        driver.switch_to.window(driver.window_handles[-1])
        i += 1
    
    values_float = []
    for value in values_list:
        if (value != NaN):
            value = float(value)
        values_float.append(value)

    data_reservas = {'Fecha': dates_list,
    'Reservas': values_float}

    df_reservas = pd.DataFrame(data_reservas, columns=['Fecha', 'Reservas'])

    print('--------------------SE EXTRAJO RESERVAS--------------')

    df_reservas = dataCleaning(df_reservas)

    return df_reservas

def tipoCambioChina(driver):
    # Inicializar el navegador
    driver.get('https://fred.stlouisfed.org/series/EXCHUS')

    WebDriverWait(driver, 5)\
    .until(EC.element_to_be_clickable((By.XPATH, 
    '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
        .click()

    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.XPATH, 
        '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
            .send_keys(Keys.CONTROL, 'a')    

    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.XPATH, 
        '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
            .send_keys(Keys.BACKSPACE)
    
    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.XPATH, 
        '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
            .send_keys('2000-01-01') 

    WebDriverWait(driver, 5)\
    .until(EC.element_to_be_clickable((By.XPATH, 
    '/html/body/div[2]/div[1]/div/div[1]/h1/div/div/button/span')))\
        .click()

    WebDriverWait(driver, 5)\
    .until(EC.element_to_be_clickable((By.XPATH, 
    '/html/body/div[2]/div[1]/div/div[1]/h1/div/div/ul/li[1]/a')))\
        .click()

    time.sleep(5)
    excel_path = getDownLoadedFileName(200, driver) #Se esperan 3 minutos a que se descargue

    try:
        archivo_excel = pd.ExcelFile(excel_path)
    except:
        print('ERROR AL EXTRAER TIPO DE CAMBIO')
        archivos = os.listdir('.')

        for archivo in archivos:
            if('EXCHUS' in archivo):
                excel_path = archivo
        
    archivo_excel = pd.ExcelFile(excel_path)
    df_cambio = archivo_excel.parse('FRED Graph', skiprows=10)

    df_cambio.rename(columns={'observation_date':'Fecha',
                        'EXCHUS':'Tipo de Cambio'},
               inplace=True)

    print('--------------SE EXTRAJO TIPO DE CAMBIO-----------------')

    df_cambio = dataCleaning(df_cambio)


    return df_cambio

def exportacionesChina(driver):
    # Inicializar el navegador
    driver.get('https://www.safe.gov.cn/en/2019/0926/1568.html')

    excel_url = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div[3]/div[4]/p/a').get_attribute('href')

    archivo_excel = pd.ExcelFile(excel_url)
    df_trade_Goods = archivo_excel.parse('In USD', skiprows=3)

    df_export = df_trade_Goods.iloc[1]

    df_export = df_export.reset_index()

    df_export = df_export.drop(0)

    df_export.rename(columns={'index':'Fecha',
                        1 :'Exportaciones'},
               inplace=True)

    wrong_dates = df_export.index[df_export['Fecha'].str.contains('Jan-Feb', na=False)].tolist()
    print(wrong_dates)

    for index in wrong_dates:
        index = index-1
        split_date = df_export.Fecha.iloc[index].split(' ')
        date_string = df_export.Fecha.iloc[index] = split_date[1] + '-02'
        df_export.Fecha.iloc[index]= datetime.strptime(str(date_string), '%Y-%m')
        value = df_export.Exportaciones.iloc[index]/2
        df_export.Exportaciones.iloc[index] = value
        df_export.Exportaciones.iloc[index-1] = value

    df_export = dataCleaning(df_export)

    print('-------------------------SE EXTRAJO EXPORTACIONES---------------------')
    
    return df_export

def liquidezSolvenciaChina(driver):
    # Inicializar el navegador
    driver.get('http://www.pbc.gov.cn/en/3688247/3688975/index.html')

    data = driver.find_elements_by_xpath('/html/body/div[6]/div[2]/div[2]/div[2]/div[2]/div/ul/li')

    df_liquidezSolvencia = pd.DataFrame()

    i = 1

    for element in data:

        year = driver.find_element_by_xpath('/html/body/div[6]/div[2]/div[2]/div[2]/div[2]/div/ul/li['+ str(i) +']/a').text            

        # Click en el año
        WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.XPATH, 
        '/html/body/div[6]/div[2]/div[2]/div[2]/div[2]/div/ul/li['+ str(i) +']/a')))\
            .click()

        year = int(year)

        if(year > 2018):
            # Click en Assets and Liabilities...
            WebDriverWait(driver, 5)\
            .until(EC.element_to_be_clickable((By.XPATH, 
            '/html/body/div[6]/div[2]/div[2]/div/div[2]/div/ul/li[3]/div/div/a')))\
                .click()

            quarterly = driver.find_elements_by_xpath('/html/body/div[6]/div[2]/div[2]/div/div[2]/div/ul/table/tbody/tr/td')
            quarterly.pop(0)

            j = 2

            for q in quarterly:

                quarter = driver.find_element_by_xpath('/html/body/div[6]/div[2]/div[2]/div/div[2]/div/ul/table/tbody/tr/td['+ str(j) +']/a').text
                
                if(not(driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/div[2]/div/div[2]/div/ul/table/tbody/tr/td['+ str(j) +']/a').get_attribute('href'))):
                    j += 1
                    continue
                else:

                    WebDriverWait(driver, 5)\
                    .until(EC.element_to_be_clickable((By.XPATH, 
                    '/html/body/div[6]/div[2]/div[2]/div/div[2]/div/ul/table/tbody/tr/td['+ str(j) +']/a')))\
                        .click()        

                    driver.switch_to.window(driver.window_handles[-1])

                    assets = isEmpty(driver.find_element_by_xpath('/html/body/div[1]/table/tbody/tr[11]/td[6]').text)
                    liabilities = isEmpty(driver.find_element_by_xpath('/html/body/div[1]/table/tbody/tr[15]/td[6]').text)
                    equities = isEmpty(driver.find_element_by_xpath('/html/body/div[1]/table/tbody/tr[19]/td[6]').text)

                    new_line = {'Año': str(year),'Trimestre': quarter,'Assets': assets, 'Liabilities': liabilities, 'Equities': equities}

                    df_liquidezSolvencia = df_liquidezSolvencia.append(new_line, ignore_index= True)

                    driver.close()

                    driver.switch_to.window(driver.window_handles[-1])

                    j += 1
                            
            WebDriverWait(driver, 5)\
            .until(EC.element_to_be_clickable((By.XPATH, 
            '/html/body/div[6]/div[1]/div/div[2]/div/div/ul/li[1]/a')))\
                .click()

            i += 1

        elif(year > 2016 and year <= 2018):
            WebDriverWait(driver, 5)\
            .until(EC.element_to_be_clickable((By.XPATH, 
            '/html/body/div[6]/div[2]/div[2]/div/div[2]/div/ul/li[5]/div/div/a')))\
                .click()
            
            WebDriverWait(driver, 5)\
            .until(EC.element_to_be_clickable((By.XPATH, 
            '/html/body/div[6]/div[2]/div[2]/div/div[2]/ul/table[2]/tbody/tr/td[2]/a')))\
                .click()

            driver.switch_to.window(driver.window_handles[-1])

            assets_uses = isEmpty(driver.find_element_by_xpath('/html/body/table/tbody/tr[13]/td[9]').text)
            assets_sources = isEmpty(driver.find_element_by_xpath('/html/body/table/tbody/tr[13]/td[10]').text)
            liabilities_uses = isEmpty(driver.find_element_by_xpath('/html/body/table/tbody/tr[18]/td[9]').text)
            liabilities_sources = isEmpty(driver.find_element_by_xpath('/html/body/table/tbody/tr[18]/td[10]').text)
            equities_uses = isEmpty(driver.find_element_by_xpath('/html/body/table/tbody/tr[23]/td[8]').text)
            equities_sources = isEmpty(driver.find_element_by_xpath('/html/body/table/tbody/tr[23]/td[9]').text)

            assets =  assets_uses + assets_sources
            liabilities = liabilities_uses + liabilities_sources
            equities = equities_uses + equities_sources

            assets_q = assets/4
            liabilities_q = liabilities/4
            equities_q = equities/4

            quarter = range(1,4)

            for q in quarter:
                new_line = {'Año': str(year),'Trimestre': 'Q'+str(q),'Assets': assets_q, 'Liabilities': liabilities_q, 'Equities': equities_q}
                df_liquidezSolvencia = df_liquidezSolvencia.append(new_line, ignore_index= True)

            print('-------------------DATA FRAME DESDE 2017----------------')

            driver.close()
            driver.switch_to.window(driver.window_handles[-1])

            WebDriverWait(driver, 5)\
            .until(EC.element_to_be_clickable((By.XPATH, 
            '/html/body/div[6]/div[1]/div/div[2]/div/div/ul/li[1]/a')))\
                .click()

            i += 1

        else:

            if(year < 2008):
                if(year == 2007):
                    WebDriverWait(driver, 5)\
                    .until(EC.element_to_be_clickable((By.XPATH, 
                    '/html/body/div[6]/div[2]/div[2]/div/div[2]/ul/table[21]/tbody/tr/td[2]/a')))\
                        .click()
                else:
                    WebDriverWait(driver, 5)\
                    .until(EC.element_to_be_clickable((By.XPATH, 
                    '/html/body/div[6]/div[2]/div[2]/div/div[2]/ul/table[16]/tbody/tr/td[2]/a')))\
                        .click()
            else:
                if(year < 2012 and year >2007):
                    WebDriverWait(driver, 5)\
                    .until(EC.element_to_be_clickable((By.XPATH, 
                    '/html/body/div[6]/div[2]/div[2]/div/div[2]/div/ul/li[4]/div/div/a')))\
                        .click()                
                else:
                    WebDriverWait(driver, 5)\
                    .until(EC.element_to_be_clickable((By.XPATH, 
                    '/html/body/div[6]/div[2]/div[2]/div/div[2]/div/ul/li[5]/div/div/a')))\
                        .click()  
                        
                WebDriverWait(driver, 5)\
                .until(EC.element_to_be_clickable((By.XPATH, 
                '/html/body/div[6]/div[2]/div[2]/div/div[2]/ul/table/tbody/tr/td[2]/a')))\
                    .click()    

            driver.switch_to.window(driver.window_handles[-1])              
            
            assets_uses = isEmpty(driver.find_element_by_xpath('/html/body/div[1]/table/tbody/tr[14]/td[9]').text)
            assets_sources = isEmpty(driver.find_element_by_xpath('/html/body/div[1]/table/tbody/tr[14]/td[10]').text)
            liabilities_uses = isEmpty(driver.find_element_by_xpath('/html/body/div[1]/table/tbody/tr[21]/td[9]').text)
            liabilities_sources = isEmpty(driver.find_element_by_xpath('/html/body/div[1]/table/tbody/tr[21]/td[10]').text)
            equities_uses = isEmpty(driver.find_element_by_xpath('/html/body/div[1]/table/tbody/tr[28]/td[9]').text)
            equities_sources = isEmpty(driver.find_element_by_xpath('/html/body/div[1]/table/tbody/tr[28]/td[10]').text)

            assets =  assets_uses + assets_sources
            liabilities = liabilities_uses + liabilities_sources
            equities = equities_uses + equities_sources

            assets_q = assets/4
            liabilities_q = liabilities/4
            equities_q = equities/4

            quarter = range(1,5)

            for q in quarter:
                new_line = {'Año': str(year),'Trimestre': 'Q'+str(q),'Assets': assets_q, 'Liabilities': liabilities_q, 'Equities': equities_q}
                df_liquidezSolvencia = df_liquidezSolvencia.append(new_line, ignore_index= True)

            print('----------------SE EXTRAJO ANTES DE 2017----------------')

            driver.close()
            driver.switch_to.window(driver.window_handles[-1])

            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)

            if(year != 2006):

                WebDriverWait(driver, 20)\
                .until(EC.element_to_be_clickable((By.XPATH, 
                '/html/body/div[6]/div[1]/div/div[2]/div/div/ul/li[1]/a')))\
                    .click()

            i += 1
        
    df_liquidez = pd.DataFrame()
    df_liquidez['Fecha'] = df_liquidezSolvencia['Año'] + '-' + df_liquidezSolvencia['Trimestre']
    df_liquidez['Liquidez'] = df_liquidezSolvencia['Liabilities']/df_liquidezSolvencia['Assets'] 
    df_solvencia =pd.DataFrame()
    df_solvencia['Fecha'] = df_liquidezSolvencia['Año'] + '-' + df_liquidezSolvencia['Trimestre']
    df_solvencia['Solvencia'] = df_liquidezSolvencia['Equities']/df_liquidezSolvencia['Assets']


    print('------------SE EXTRAJO LIQUIDEZ Y SOLVENCIA---------------')

    df_liquidez = dataCleaning(df_liquidez)
    df_solvencia = dataCleaning(df_solvencia)

    return (df_liquidez, df_solvencia)
    
def portafolioChina(driver):
    # Inicializar el navegador
    driver.get('https://www.safe.gov.cn/en/2019/0329/1496.html')

    excel_url = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div[3]/div[4]/p/a').get_attribute('href')

    archivo_excel = pd.ExcelFile(excel_url)
    df_payments = archivo_excel.parse('quarterly(USD)', skiprows=3)

    df_portfolio = df_payments.iloc[99]

    df_portfolio = df_portfolio.reset_index()

    df_portfolio = df_portfolio.drop(0)

    df_portfolio.rename(columns={'index':'Fecha',
                       99 :'Portafolio'},
               inplace=True)

    print('-------------------------SE EXTRAJO PORTAFOLIO--------------------')

    df_portfolio = dataCleaning(df_portfolio)

    return df_portfolio
           
def deudaChina(driver):
    # Inicializar el navegador
    driver.get('https://www.safe.gov.cn/en/2018/0329/1412.html')

    excel_url = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div[3]/div[4]/p[1]/span/a[2]').get_attribute('href')

    archivo_excel = pd.ExcelFile(excel_url)
    df_external_debt = archivo_excel.parse('Sheet1', skiprows=1)

    df_debt = df_external_debt.iloc[58]

    df_debt = df_debt.reset_index()

    df_debt.drop([0,1], inplace = True)

    df_debt.rename(columns={'index':'Fecha',
                        58 :'Deuda Externa'},
               inplace=True)

    print('-------------------------SE EXTRAJO DEUDA EXTERNA--------------------')

    df_debt = dataCleaning(df_debt)

    return df_debt

def pibChina(driver):
    # Inicializar el navegador
    driver.get('https://fred.stlouisfed.org/series/CHNGDPNQDSMEI')

    WebDriverWait(driver, 5)\
    .until(EC.element_to_be_clickable((By.XPATH, 
    '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
        .click()

    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.XPATH, 
        '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
            .send_keys(Keys.CONTROL, 'a')    

    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.XPATH, 
        '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
            .send_keys(Keys.BACKSPACE)
    
    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.XPATH, 
        '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
            .send_keys('2000-01-01') 

    WebDriverWait(driver, 5)\
    .until(EC.element_to_be_clickable((By.XPATH, 
    '/html/body/div[2]/div[1]/div/div[1]/h1/div/div/button/span')))\
        .click()

    WebDriverWait(driver, 5)\
    .until(EC.element_to_be_clickable((By.XPATH, 
    '/html/body/div[2]/div[1]/div/div[1]/h1/div/div/ul/li[1]/a')))\
        .click()

    time.sleep(5)
    excel_path = getDownLoadedFileName(200, driver) #Se esperan 3 minutos a que se descargue
    

    try:
        archivo_excel = pd.ExcelFile(excel_path)
    except:
        print('ERROR AL EXTRAER PIB')
        archivos = os.listdir('.')

        for archivo in archivos:
            if('CHNGDP' in archivo):
                excel_path = archivo
                break

    
    archivo_excel = pd.ExcelFile(excel_path)
    df_pib = archivo_excel.parse('FRED Graph', skiprows=10)

    df_pib.rename(columns={'observation_date':'Fecha',
                        'CHNGDPNQDSMEI':'PIB'},
               inplace=True)

    print('--------------SE EXTRAJO PIB-----------------')   

    df_pib = dataCleaning(df_pib) 

    return df_pib

def inflacionChina(driver):
    # Inicializar el navegador
    driver.get('https://fred.stlouisfed.org/series/CHNCPIALLQINMEI')

    WebDriverWait(driver, 5)\
    .until(EC.element_to_be_clickable((By.XPATH, 
    '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
        .click()

    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.XPATH, 
        '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
            .send_keys(Keys.CONTROL, 'a')    

    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.XPATH, 
        '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
            .send_keys(Keys.BACKSPACE)
    
    WebDriverWait(driver, 5)\
        .until(EC.element_to_be_clickable((By.XPATH, 
        '/html/body/div[2]/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/input')))\
            .send_keys('2000-01-01') 

    WebDriverWait(driver, 5)\
    .until(EC.element_to_be_clickable((By.XPATH, 
    '/html/body/div[2]/div[1]/div/div[1]/h1/div/div/button/span')))\
        .click()

    WebDriverWait(driver, 5)\
    .until(EC.element_to_be_clickable((By.XPATH, 
    '/html/body/div[2]/div[1]/div/div[1]/h1/div/div/ul/li[1]/a')))\
        .click()
    
    time.sleep(5)
    excel_path = getDownLoadedFileName(200, driver) #Se esperan 3 minutos a que se descargue

    try: 
        archivo_excel = pd.ExcelFile(excel_path)
    except:
        print('ERROR AL EXTRAER INFLACION')
        archivos = os.listdir('.')

        for archivo in archivos:
            if('CHNCPI' in archivo):
                excel_path = archivo

    archivo_excel = pd.ExcelFile(excel_path)

    df_inflacion = archivo_excel.parse('FRED Graph', skiprows=10)

    df_inflacion.rename(columns={'observation_date':'Fecha',
                        'CHNCPIALLQINMEI':'Inflacion'},
               inplace=True)

    driver.close()

    print('--------------SE EXTRAJO INFLACION-----------------')  

    df_inflacion = dataCleaning(df_inflacion)  

    return df_inflacion

def tasaCrecimiento(df, columna):
    tasa_crecimiento_list = [NaN]
    for i in range(1, len(df[columna]-1)):
        v2 = df.iloc[i][columna]
        v1 = df.iloc[i-1][columna]
        tasa_crecimiento = ((v2-v1)/v1)*100
        tasa_crecimiento_list.append(tasa_crecimiento)
    df['Tasa Crecimiento'] = tasa_crecimiento_list    
    return df

def text_format(val):
    color = 'white'
    if (val == 'Crisis'):
      color = '#ff0000'
    elif (val == 'Alerta'):
      color = '#ffff00'
    return 'background-color: %s' % color

def espisodios(df, columns_names):
    df['Media Movil']=df[columns_names[-1]].rolling(window=8).mean()
    df['D.E']=df[columns_names[-1]].rolling(window=8).std()
    df['Sistem Alertas'] = (df[columns_names[-1]]-df['Media Movil'])/df['D.E']
    conditionlist = []

    # Indicadores en alerta y crisis con valores negativos
    if(columns_names[0] == 'Liquidez' or columns_names[0] == 'Solvencia' or 
    columns_names[0] == 'Reservas' or columns_names[0] == 'PIB' or columns_names[0] == 'Inversión de Portafolio'):
        conditionlist = [
            ((-1.5 >= df['Sistem Alertas'])) & ((df['Sistem Alertas'] > -2.0)),
            (-2.0 >= df['Sistem Alertas']),
            (-1.5 < df['Sistem Alertas'])]
    # Indicadores en alerta y crisis con valores positivos
    else:
        conditionlist = [
            ((1.5 <= df['Sistem Alertas'])) & ((df['Sistem Alertas'] < 2.0)),
            (2.0 <= df['Sistem Alertas']),
            (1.5 > df['Sistem Alertas'])]
    choicelist = ['Alerta', 'Crisis', 'Sin Episodio']
    df['Episodio'] = np.select(conditionlist, choicelist, default='Not Specified')
    return df

def episode_count(df, indicador):
  crisis = 0
  alertas = 0
  for episodio in df['Episodio']:
    if(episodio == 'Alerta'):
      alertas += 1
    elif (episodio == 'Crisis'):
      crisis += 1
  episode_quantity = [indicador, alertas, crisis]
  return episode_quantity


