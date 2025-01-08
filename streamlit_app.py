import pandas as pd
import streamlit as st
import xlsxwriter
import script_scrapper as scraper
import io

if 'data' not in st.session_state:
    st.session_state.data = None

if 'data_scrap' not in st.session_state:
    st.session_state.data_scrap = None

st.header('Web Scraping', divider='violet')

col1, col2, col3 = st.columns(3)

btn_obtener = col1.button('Obtener Datos')
if btn_obtener:
    with st.spinner('Obteniendo datos...'):
        data, data_scrap = scraper.main()
    st.session_state.data = data
    st.session_state.data_scrap = data_scrap

if st.session_state.data is not None:
    st.dataframe(st.session_state.data)

    excel_file = io.BytesIO()
    st.session_state.data.to_excel(excel_file)
    excel_file.seek(0)

    col3.download_button(
        label="Descargar Datos Procesados",
        data=excel_file,
        file_name='productos.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
else:
    btn_descargar = col3.button('Descargar Datos Procesados')
    if btn_descargar:
        st.warning('Primero debes obtener los datos.')

if st.session_state.data_scrap is not None:

    excel_scrap = io.BytesIO()
    st.session_state.data_scrap.to_excel(excel_scrap)
    excel_scrap.seek(0)

    col2.download_button(
        label="Descargar Datos Obtenidos",
        data=excel_scrap,
        file_name='productos_scrappeados.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
else:
    btn_scrapeado = col2.button('Descargar Datos Obtenidos')
    if btn_scrapeado:
        st.warning('Primero debes obtener los datos.')