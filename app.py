import pandas as pd
import streamlit as st
import io
import scraper  # Asegúrate de tener este módulo con la función main()

# Estado de sesión para manejar los datos obtenidos
if 'data' not in st.session_state:
    st.session_state.data = None

# Encabezado de la aplicación
st.header('Web Scraping de Supermercados', divider='violet')

# Columnas para organizar los botones
col1, col2, col3 = st.columns(3)

# Botón para obtener los datos
btn_obtener = col1.button('Obtener Datos')
if btn_obtener:
    with st.spinner('Obteniendo datos...'):
        # Ejecuta el scraping y clasifica los productos en scraper.main()
        data = scraper.main()
        # Clasificar cada producto en tipo y descripción
        data[['Tipo', 'Descripción']] = data['Producto'].apply(
            lambda producto: pd.Series(scraper.clasificar_producto(producto))
        )
    st.session_state.data = data

# Verifica si ya se obtuvieron los datos para habilitar la descarga
if st.session_state.data is not None:
    # Crear un archivo Excel en memoria para descargar
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        # Guarda el DataFrame clasificado en una hoja de Excel
        st.session_state.data.to_excel(writer, index=False, sheet_name='Productos Clasificados')
    excel_file.seek(0)
    
    # Botón para descargar los datos
    col3.download_button(
        label="Descargar Datos Clasificados",
        data=excel_file,
        file_name='productos_clasificados.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
else:
    col3.button('Descargar Datos', disabled=True)
    st.warning('Primero debes obtener los datos.')
