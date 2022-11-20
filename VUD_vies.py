# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 13:23:56 2021

@author: User
"""


# txt = "ATU10592107"


import streamlit as st
import pandas as pd
from io import BytesIO
# from pyxlsb import open_workbook as open_xlsb
from pathlib import Path
from suds.client import Client
import os
from datetime import datetime

st.set_page_config(page_title="VUD",page_icon="vud.ico",layout="wide")


st.write(
    """
# 📊 V.U.D. Modelo Búsqueda de VIES 
Subir fichero "XLSX" con los VIES A BUSCAR en página "Hoja1".
"""
)

valid_country=(
"AT",
"BE",
"BG",
"CY",
"CZ",
"DE",
"DK",
"EE",
"EL",
"ES",
"FI",
"FR",
"HR",
"HU",
"IE",
"IT",
"LT",
"LU",
"LV",
"MT",
"NL",
"PL",
"PT",
"RO",
"SE",
"SI",
"SK",
"XI")

url="http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"
client = Client(url)

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data


# no lo borramos para que cuando nos cape podamos seguir anexando
if (os.path.isfile('resultados_busqueda_vies.csv')):
      os.remove('resultados_busqueda_vies.csv')

file_w = open("resultados_busqueda_vies.csv","x",encoding='latin1')
# file_w = open("resultados_busqueda_vies.csv","x",encoding='utf-32')

file_w.write("VIES;")
file_w.write("Código país;")
file_w.write("Número de IVA intra;")
file_w.write("Fecha de solicitud;")
file_w.write("Válido;")
file_w.write("Razón social;")
file_w.write("Dirección;")
file_w.write("\n")
file_w.close()  



uploaded_file = st.file_uploader("Upload Excel", type=".xlsx")

if uploaded_file:
    # file =open(uploaded_file,"r")
    # file = pd.read_csv(uploaded_file)
    
    df = pd.read_excel(uploaded_file, sheet_name='Hoja1')

    file_name = Path(uploaded_file.name).stem
    
    now = datetime.now()
    new_file_name_csv=file_name + "_" + str(now.year) + str(now.month) + str(now.day) + "_" + str(now.hour) +str(now.minute) + ".csv"
    new_file_name_xlsx=file_name + "_" + str(now.year) + str(now.month) + str(now.day) + "_" + str(int(now.hour)*100 +int(now.minute)) + ".xlsx"

    for i in range(len(df)):
        myvies=df['VIES'][i]
        # st.write(myvies)
        # myvies=myvies[2:-3]
        # st.write(myvies)
        # myvies=myvies.strip(' \n')
        # st.write(myvies)
        try:
            pais=myvies[0:2]
            num=myvies[2:]
        except Exception :
            pais=""
            num=""

        try:
            r=client.service.checkVat(pais, num)
            address=r.address.strip(' \n')
            address=address.replace("\n","")
                
            st.write(str(myvies) + " :" + str(r.valid))

            
            file_w = open("resultados_busqueda_vies.csv", "a",encoding='latin1')
            file_w.write(f"{myvies};")
            file_w.write(f"{r.countryCode};")
            file_w.write(f"{r.vatNumber};")
            file_w.write(f"{r.requestDate};")
            file_w.write(f"{r.valid};")
            file_w.write(f"{r.name};")
            file_w.write(f"{address}")
             
            file_w.write("\n")
            file_w.close()  
        except Exception :
            st.write(str(myvies) + " : No Válido")
            file_w = open("resultados_busqueda_vies.csv", "a",encoding='latin1')
            file_w.write(f"{myvies};")
            file_w.write("No válido;")
            file_w.write("No válido;")
            file_w.write("No válido;")
            file_w.write("No válido;")
            file_w.write("No válido;")
            file_w.write("No válido")
             
            file_w.write("\n")
            file_w.close()
    file_w = open("resultados_busqueda_vies.csv",encoding='latin1')

    st.download_button(label='📥 Bajar los resultados actuales en CSV',data=file_w, file_name=new_file_name_csv )                    
    file_w.close()          
    
    
    df_escrito=pd.read_csv('resultados_busqueda_vies.csv',sep=';',encoding='latin1')
    file_x=to_excel(df_escrito)
    st.download_button(label='📥 Bajar los resultados actuales en EXCEL',data=file_x, file_name=new_file_name_xlsx)   
            
