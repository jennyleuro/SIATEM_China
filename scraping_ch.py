import funciones_ch as fch
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

# Opciones de navegación
driver = fch.browserOptions("D:\Chrome driver\chromedriver.exe")


# Exracción de los datos de China
df_reservas = fch.reservasChina(driver)
df_tipo_cambio = fch.tipoCambioChina(driver)
df_exportaciones =fch.exportacionesChina(driver)
(df_liquidez, df_solvencia) = fch.liquidezSolvenciaChina(driver)
df_portafolio = fch.portafolioChina(driver)
df_deuda = fch.deudaChina(driver)
df_pib = fch.pibChina(driver)
df_inflacion = fch.inflacionChina(driver)

indicadores_mensuales = [df_reservas, df_tipo_cambio, df_exportaciones]

writer = pd.ExcelWriter('indicadores_trimestrales_CHINA.xlsx')

for indicador in indicadores_mensuales:
  quarterly = indicador.resample('Q').mean()
  quarterly = quarterly.reset_index()
  lista_fechas = []
  for fecha in quarterly['Fecha']:
    dias = int(fecha.strftime('%d'))-1
    fecha_nueva = fecha - datetime.timedelta(days = dias)
    lista_fechas.append(fecha_nueva)
  quarterly['Fecha'] = lista_fechas
  quarterly = quarterly.set_index('Fecha')
  columns_names = list(quarterly.columns.values)
  quarterly.to_excel(writer, sheet_name = columns_names[-1])

indicadores_trim_Q = [df_liquidez, df_solvencia, df_portafolio, df_deuda]

for indicador in indicadores_trim_Q:
    indicador = indicador.reset_index()
    lista_fechas = []
    for fecha in indicador['Fecha']:
        if('Q1' in fecha):
            fecha = fecha[0:4]+'-03'
        elif('Q2' in fecha):
            fecha = fecha[0:4]+'-06'
        elif('Q3' in fecha):
            fecha = fecha[0:4]+'-09'
        elif('Q4' in fecha):
            fecha = fecha[0:4]+'-12'
        lista_fechas.append(fecha)
    indicador['Fecha'] = lista_fechas
    indicador['Fecha'] = pd.to_datetime(indicador['Fecha'])
    indicador = indicador.set_index('Fecha')
    columns_names = list(indicador.columns.values)
    indicador.to_excel(writer, sheet_name = columns_names[-1])

indicadores_trim_num = [df_pib, df_inflacion]

for indicador in indicadores_trim_num:
    indicador = indicador.reset_index()
    lista_fechas = []
    for fecha in indicador['Fecha']:
        fecha_nueva = fecha - relativedelta(months = 1)
        lista_fechas.append(fecha_nueva)
    indicador['Fecha'] = lista_fechas
    indicador = indicador.set_index('Fecha')
    indicador = indicador.sort_index()
    columns_names = list(indicador.columns.values)
    indicador.to_excel(writer, sheet_name = columns_names[-1])


writer.save()

print('SE EXTRAJO Y GUARDO LA INFORMACIÓN')



