import pandas as pd
import funciones_ch as fch

excel_doc = 'indicadores_trimestrales_CHINA.xlsx'
archivo_excel = pd.ExcelFile(excel_doc)

try:
    df_reservas = archivo_excel.parse('Reservas', index_col='Fecha')
    df_tipo_cambio = archivo_excel.parse('Tipo de Cambio', index_col='Fecha')
    df_exportaciones = archivo_excel.parse('Exportaciones', index_col='Fecha')
    df_liquidez = archivo_excel.parse('Liquidez', index_col='Fecha')
    df_solvencia = archivo_excel.parse('Solvencia', index_col='Fecha')
    df_portafolio = archivo_excel.parse('Portafolio', index_col='Fecha')
    df_deuda = archivo_excel.parse('Deuda Externa', index_col='Fecha')
    df_PIB = archivo_excel.parse('PIB', index_col='Fecha')
    df_inflacion = archivo_excel.parse('Inflacion', index_col='Fecha')
except:
    print('Error al cargar los datos')

indicadores_dolares = [df_reservas, df_PIB, df_portafolio]

#Calculo de tasas de crecimiento
for indicador in indicadores_dolares:
    columns_names = list(indicador.columns.values)
    indicador = fch.tasaCrecimiento(indicador, columns_names[-1])

#Deuda Externa/ Exportaciones
df_deuda_export = pd.DataFrame()
df_deuda_export['Deuda_Export'] = df_deuda['Deuda Externa']/df_exportaciones['Exportaciones']

indicadores_listos = [df_deuda_export, df_liquidez, df_solvencia, df_PIB, df_portafolio, df_reservas, df_tipo_cambio, df_inflacion]

writer = pd.ExcelWriter('episodios_indicadores_CHINA.xlsx')

df_quantity = pd.DataFrame(columns= ['Indicador', 'Alertas', 'Crisis'])

df_quantity = pd.DataFrame(columns= ['Indicador', 'Alertas', 'Crisis'])

for indicador in indicadores_listos:
    columns_names = list(indicador.columns.values)
    indicador = fch.espisodios(indicador, columns_names)
    list_quantity = fch.episode_count(indicador, columns_names[0])
    df_quantity=df_quantity.append({'Indicador' : list_quantity[0] , 'Alertas' : list_quantity[1], 'Crisis' : list_quantity[2]} , ignore_index=True)
    indicador = indicador.style.applymap(fch.text_format)
    indicador.to_excel(writer, sheet_name = columns_names[0])
   
df_quantity.to_excel(writer, sheet_name = 'Cantidad Episodios')

writer.save()

print('se calcularon y guardaron los episodios de los indicadores')
