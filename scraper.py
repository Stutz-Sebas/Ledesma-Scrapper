import pandas as pd
import numpy as np
import requests
import time
import csv
import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def main():
    archivo = 'WebScraping\Estructura_Con_Precio_Oferta_0.csv'
    df_plantilla = pd.read_csv(archivo, header=[0, 1, 2], index_col=[0, 1])
    
    df_cordiez = cordiez()
    df_carre = carrefour()
    #df_coto = coto()
    #productos_scrapeados = pd.concat([df_cordiez, df_carre, df_coto])
    productos_scrapeados = pd.concat([df_cordiez, df_carre])

    productos_scrapeados[['Tipo', 'Descripción']] = productos_scrapeados['Producto'].apply(
        lambda producto: pd.Series(clasificar_producto(producto))
    )
    
    productos_scrapeados.to_csv('Prueba.csv')

    cargar_precios_en_planilla(df_plantilla, productos_scrapeados)

    return df_plantilla, productos_scrapeados

def normalizar_texto(texto):
    # Convierte el texto en minusculas y elimina acentos
    import unicodedata
    texto = texto.lower()
    texto = ''.join(
        (c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    )
    return texto

def clasificar_producto(nombre_producto):
    clasificaciones = {
        "AZÚCAR LIGHT": {
            "palabras_tipo": ["azucar", "light"],
            "descripciones": {
                "Ledesma": ["ledesma"],
                "Hileret 250 gr": ["250"],
                "Hileret": ["hileret"],
                "EqualSwet Stevia": ["equalswet"],
                r"Chango 50% calorías": ["chango"]
            }
        },
        "RUBIA MASCABO": {
            "palabras_tipo": ["mascabo", "orgánica"],
            "descripciones": {
                "Ledesma Mascabo 800gr": ["ledesma"],
                "Chango Orgánica 1kg": ["chango"]
            }
        },
        "POLVOS 50 SOBRES": {
            "palabras_tipo": ["50 sobres", "50 un", "50 unidades", "50 u"],
            "descripciones": {
                "Ledesma": ["ledesma"],
                "Hileret": ["hileret"],
                "Cañuelas": ["canuelas", "cañuelas"],
                "LIV": ["liv"],
                "Equal": ["equalswet", "equal"],
                "Tuy": ["tuy"]
            }
        },
        "POLVOS 100 SOBRES": {
            "palabras_tipo": ["100 sobres", "100 un", "100 unidades", "100 u"],
            "descripciones": {
                "Ledesma": ["ledesma"],
                "Hileret": ["hileret"],
                "Cañuelas": ["canuelas", "cañuelas"],
                "LIV": ["liv"],
                "Equal": ["equalswet", "equal"],
                "Tuy": ["tuy"]
            }
        },
        "POLVOS 200 SOBRES": {
            "palabras_tipo": ["200 sobres", "200 un", "200 unidades", "200 u"],
            "descripciones": {
                "Ledesma": ["ledesma"],
                "Hileret": ["hileret"],
                "LIV": ["liv"],
                "Equal": ["equalswet", "equal"],
                "Tuy": ["tuy"]
            }
        },
        "LIQ. SUCRA 100 a 300 cc": {
            "palabras_tipo": ["sucralosa", "sucra", "sukra", "zucra"],
            "descripciones": {
                "Equal": ["equal"],
                "Hileret": ["hileret"],
                "Cañuelas": ["canuelas", "cañuelas"],
                "LIV": ["liv"],
                "Tuy": ["tuy"]
            }
        },
        "LIQ, STEVIA 100 a 300 cc": {
            "palabras_tipo": ["stevia"],
            "descripciones": {
                "Ledesma": ["ledesma"],
                "Hileret": ["hileret"],
                "Cañuelas": ["canuelas", "cañuelas"],
                "LIV": ["liv"],
                "Equal": ["equalswet"],
                "Tuy": ["tuy"]
            }
        },
        "LIQ. CLÁSICO 100 a 300 cc": {
            "palabras_tipo": ["liquido", "clásico", "mate", "sweet"],
            "descripciones": {
                "Cañuelas Clasico 200 ml": ["cañuelas", "canuelas"],
                "Hileret Clasico 250 ml": ["clasico"],
                "Hileret mate 200 ml": ["mate"],
                "Hileret Sweet 200 cc": ["sweet"],
                "LIV Clasico 200 ml": ["liv"],
                "Chuker Clasico 200 ml": ["chucker"]
            }
        },
        "AZÚCAR BLANCA": {
            "palabras_tipo": ["azucar", "común", "molida", "comun"],
            "descripciones": {
                "Ledesma Clasica": ["clasica"],
                "Ledesma Superior": ["superior"],
                "Domino": ["domino"],
                "Azucel 1kg": ["azucel"],
                "Crystal": ["crystal"],
                "Providencia 1kg": ["providencia"],
                "Check (changomas)": ["check"],
                "Ancaste 1kg": ["ancaste"],
                "Fronterita 1kg": ["fronterita"],
                "Dul-C 1kg": ["dul-c"],
                "Bella Vista 1kg": ["bella vista"],
            }
        }
    }

    tipo = "Desconocido"
    descripcion = "Desconocido"

    nombre_producto = normalizar_texto(nombre_producto)

    for tipo_clave, tipo_info in clasificaciones.items():
        # Si es "AZÚCAR LIGHT", revisa que esten presentes ambas palabras
        if tipo_clave == "AZÚCAR LIGHT":
            if all(palabra in nombre_producto for palabra in tipo_info["palabras_tipo"]):
                tipo = tipo_clave
        elif any(palabra in nombre_producto for palabra in tipo_info["palabras_tipo"]):
            # Si el tipo es "LIQ.", se valida el volumen
            if "LIQ." in tipo_clave:
                medicion_match = re.search(r"(\d+)\s?(cc|ml)", nombre_producto)
                if medicion_match:
                    cantidad = int(medicion_match.group(1))
                    if not (100 <= cantidad <= 300):
                        continue
            
            tipo = tipo_clave
            for desc_clave, palabras_clave in tipo_info["descripciones"].items():
                if any(palabra in nombre_producto for palabra in palabras_clave):
                    descripcion = desc_clave
                    break
            break

    return tipo, descripcion


def cargar_precios_en_planilla(planilla, datos_scrapeados):
    supermercados_nacionales = ['Coto', 'CRF']
    supermercados_interior = ['Cordiez (CBA)']

    for _, row in datos_scrapeados.iterrows():
        tipo = row['Tipo']
        descripcion = row['Descripción']
        supermercado = row['Supermercado']
        precio = row['Precio']

        if tipo == "Desconocido" or descripcion == "Desconocido":
            continue

        if supermercado in supermercados_nacionales:
            columna = ('Supermercados Nacionales', supermercado, 'Precio')
        elif supermercado in supermercados_interior:
            columna = ('Supermercados Interior', supermercado, 'Precio')

        planilla.loc[(tipo, descripcion), columna] = precio
        
def cordiez():
    url = 'https://www.cordiez.com.ar/desayuno-y-merienda/azucar-y-edulcorante/'

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height
    
    
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    contenedor = soup.find('div', class_='row', attrs={'data-next': '_next_searched_products'})
    productos = contenedor.find_all('div', class_='product')



    productos_lista = []
    supermercado = 'Cordiez (CBA)'

    for producto in productos:
        titulo_div = producto.find('h5')
        nombre = titulo_div.text.strip() if titulo_div else 'Nombre no encontrado'
        
        precio_contenedor = producto.find('div', class_='offer-price text-price mb-0')
        
        if precio_contenedor:
            span = precio_contenedor.find('span')
            if span:
                span.extract()
            precio_texto = precio_contenedor.get_text(strip=True).replace(u'\xa0', u' ')

            precio = float(precio_texto.replace('$', '').replace('.', '').replace(',', '.').strip())
        else:
            precio = np.nan

        productos_lista.append([supermercado, nombre, precio])

    df = pd.DataFrame(productos_lista, columns=['Supermercado', 'Producto', 'Precio'])
    return df

def carrefour():
    url = 'https://www.carrefour.com.ar/Desayuno-y-merienda/Azucar-y-endulzantes/Azucar'

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    # contenedor = soup.find('div', class_='pr0  vtex-flex-layout-0-x-stretchChildrenWidth   flex')
    productos = soup.find_all('div', class_='valtech-carrefourar-search-result-2-x-galleryItem valtech-carrefourar-search-result-2-x-galleryItem--normal pa4')

    productos_lista = []
    supermercado = 'CRF'

    for producto in productos:
        titulo_div = producto.find('span', class_='vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body')
        articulo = titulo_div.text.strip() if titulo_div else 'Nombre no encontrado'
        
        precio_contenedor = producto.find('span', class_='valtech-carrefourar-product-price-0-x-currencyContainer')
        
        if precio_contenedor:
            precio_texto = precio_contenedor.get_text(strip=True).replace(u'\xa0', u' ')

            precio = float(precio_texto.replace('$', '').replace('.', '').replace(',', '.').strip())
        else:
            precio = np.nan

        productos_lista.append([supermercado, articulo, precio])

    df = pd.DataFrame(productos_lista, columns=['Supermercado', 'Producto', 'Precio'])
    return df

def coto():
    url = 'https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-almac%C3%A9n-endulzantes-az%C3%BAcar/_/N-1w1x9xa'

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    contenedor = soup.find('ul', class_='grid')
    productos = contenedor.find_all('li', class_='clearfix first')

    productos_lista = []
    supermercado = 'Coto'

    for producto in productos:
        titulo_div = producto.find('div', class_='descrip_full')
        articulo = titulo_div.text.strip() if titulo_div else 'Nombre no encontrado'
        
        precio_contenedor = producto.find('span', class_='atg_store_newPrice')
        
        if precio_contenedor:
            precio_texto = precio_contenedor.get_text(strip=True).replace(u'\xa0', u' ')

            precio = float(precio_texto.replace('$', '').replace('.', '').replace(',', '.').strip())
        else:
            precio = np.nan

        productos_lista.append([supermercado, articulo, precio])

    df = pd.DataFrame(productos_lista, columns=['Supermercado', 'Producto', 'Precio'])
    return df


"""
def disco():
    url = 'https://www.disco.com.ar/azucar?_q=azucar&map=ft'

    driver = webdriver.Chrome()
    driver.get(url)

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    contenedor = soup.find('div', class_='vtex-search-result-3-x-gallery vtex-search-result-3-x-gallery--grid flex flex-row flex-wrap items-stretch bn ph1 na4 pl9-l')
    productos = contenedor.find_all('div', class_='vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4')

    productos_lista = []
    supermercado = 'Disco'

    for producto in productos:
        titulo_div = producto.find('span', class_='vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body')
        articulo = titulo_div.text.strip() if titulo_div else 'Nombre no encontrado'
        
        precio_contenedor = producto.find('div', class_='discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w')
        
        if precio_contenedor:
            precio_texto = precio_contenedor.get_text(strip=True).replace(u'\xa0', u' ')

            precio = float(precio_texto.replace('$', '').replace('.', '').replace(',', '.').strip())
        else:
            precio = np.nan

        productos_lista.append([supermercado, articulo, precio])

    df = pd.DataFrame(productos_lista, columns=['Supermercado', 'Producto', 'Precio'])
    return df"""