import pandas as pd
import numpy as np
import requests
import time
import csv
import datetime
import re
import gzip
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def main():
    archivo = 'WebScraping\Estructura_Con_Precio_Oferta_0.csv'
    df_plantilla = pd.read_csv(archivo, header=[0, 1, 2], index_col=[0, 1])
    
    df_cordiez = cordiez()
    #df_carre = carrefour()
    #df_coto = coto()
    #productos_scrapeados = pd.concat([df_cordiez, df_carre, df_coto])
    productos_scrapeados = pd.concat([df_cordiez])
    
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
    url = 'https://www.cordiez.com.ar/api/catalog_system/pub/products/search/desayuno-y-merienda/azucar-y-edulcorante/?&_from=0&_to=49&O=OrderByScoreDESC'
    
    # Encabezados (simula el navegador)
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 'VtexRCSessionIdv7=6e9d51a5-c74b-44c9-9971-b0bb8ba81dde; VtexRCMacIdv7=b09b54e3-c9ec-4d47-b552-e10c120cf012; _gcl_au=1.1.1492931608.1735305151; _gid=GA1.3.174540012.1735305151; __kdtv=t%3D1735305151397%3Bi%3D29924344dc044809a3213ead87a593f186e41744; _kdt=%7B%22t%22%3A1735305151397%2C%22i%22%3A%2229924344dc044809a3213ead87a593f186e41744%22%7D; VTEXSC=sc=1; ISSMB=ScreenMedia=0&UserAcceptMobile=False; SGTS=8915406B30546143C61DBAC54C4F3D27; CheckoutOrderFormOwnership=; vtex_segment=eyJjYW1wYWlnbnMiOm51bGwsImNoYW5uZWwiOiIxIiwicHJpY2VUYWJsZXMiOm51bGwsInJlZ2lvbklkIjpudWxsLCJ1dG1fY2FtcGFpZ24iOm51bGwsInV0bV9zb3VyY2UiOm51bGwsInV0bWlfY2FtcGFpZ24iOm51bGwsImN1cnJlbmN5Q29kZSI6IkFSUyIsImN1cnJlbmN5U3ltYm9sIjoiJCIsImNvdW50cnlDb2RlIjoiQVJHIiwiY3VsdHVyZUluZm8iOiJlcy1BUiIsImNoYW5uZWxQcml2YWN5IjoicHVibGljIn0; _fbp=fb.2.1735305151872.799355841648030922; vtex_session=eyJhbGciOiJFUzI1NiIsImtpZCI6IjgxODcwMTM5LWNmMTYtNGRiNi1hZGUzLWQ4NDY3ODgyYTMwYyIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50LmlkIjpbXSwiaWQiOiJiMzJlODcyYS0wM2E3LTRiY2QtYmNkNS00OTg2NTBmYWRjODIiLCJ2ZXJzaW9uIjoyLCJzdWIiOiJzZXNzaW9uIiwiYWNjb3VudCI6InNlc3Npb24iLCJleHAiOjE3MzU5OTYzNTEsImlhdCI6MTczNTMwNTE1MSwianRpIjoiODVjODQwOTItMDMxZi00YzViLTgwYmItZjc0NjM2MGFmNzgwIiwiaXNzIjoic2Vzc2lvbi9kYXRhLXNpZ25lciJ9.CP467FN9KUCLKvjI5ULnhZtIKfqU_52zfp78eM64m0t1bKrY0JiJY8HvtfAWMikleRqGp1oBKrgroCu_CjODFg; checkout.vtex.com=__ofid=1a68c780b971418db8416b6362253a0d; _gat_UA-125149805-1=1; _ga_NY76PB0BZ5=GS1.1.1735305151.1.1.1735305246.59.0.0; _ga=GA1.1.1972036693.1735305151; janus_sid=8e6ef8ce-a900-44ea-bbe1-d2301a538f6c',  # Coloca todas las cookies necesarias aquí
        'Host': 'www.cordiez.com.ar',
        'Referer': 'https://www.cordiez.com.ar/desayuno-y-merienda/azucar-y-edulcorante/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    
    response = requests.get(url)

    content_type = response.headers.get("Content-Type", "")
    print(f"Content-Type: {content_type}")

    # Si el contenido es JSON
    if "application/json" in content_type:
        try:
            # Parsear directamente como JSON
            data_json = response.json()
            print("Datos JSON cargados correctamente.")
        except json.JSONDecodeError as e:
            print(f"Error al cargar JSON: {e}")
            return pd.DataFrame()  # Retornar un DataFrame vacío en caso de error
    else:
        print("El contenido no es JSON. Aquí está el texto sin procesar:")
        print(response.text)
        return pd.DataFrame()
    
    productos_lista = []
    supermercado = 'Cordiez (CBA)'

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        for producto in data_json:  # Iterar sobre la lista de productos
            nombre = producto.get('productName', 'Nombre no encontrado')
            marca = producto.get('brand', 'Marca no encontrada')
            for item in producto.get('items', []):  # Itera sobre cada elemento en 'items'
                for seller in item.get('sellers', []):  # Itera sobre cada vendedor en 'sellers'
                    precioBase = seller.get('commertialOffer', {}).get('PriceWithoutDiscount', None)
                    precioOferta = seller.get('commertialOffer', {}).get('Price', None)
                    productos_lista.append([supermercado, nombre, marca, precioBase, precioOferta])
        
        # Crear el DataFrame después de llenar la lista
        df = pd.DataFrame(productos_lista, columns=['Supermercado', 'Producto', 'Marca', 'Precio', 'Oferta'])
        return df
    
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return pd.DataFrame()

def carrefour():
    url = r'https://www.carrefour.com.ar/_v/segment/graphql/v1?workspace=master&maxAge=short&appsEtag=remove&domain=store&locale=es-AR&__bindingId=ecd0c46c-3b2a-4fe1-aae0-6080b7240f9b&operationName=productSearchV3&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%229177ba6f883473505dc99fcf2b679a6e270af6320a157f0798b92efeab98d5d3%22%2C%22sender%22%3A%22vtex.store-resources%400.x%22%2C%22provider%22%3A%22vtex.search-graphql%400.x%22%7D%2C%22variables%22%3A%22eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6dHJ1ZSwic2t1c0ZpbHRlciI6IkFMTF9BVkFJTEFCTEUiLCJzaW11bGF0aW9uQmVoYXZpb3IiOiJkZWZhdWx0IiwiaW5zdGFsbG1lbnRDcml0ZXJpYSI6Ik1BWF9XSVRIT1VUX0lOVEVSRVNUIiwicHJvZHVjdE9yaWdpblZ0ZXgiOmZhbHNlLCJtYXAiOiJjLGMsYyIsInF1ZXJ5IjoiZGVzYXl1bm8teS1tZXJpZW5kYS9henVjYXIteS1lbmR1bHphbnRlcy9henVjYXIiLCJvcmRlckJ5IjoiT3JkZXJCeVNjb3JlREVTQyIsImZyb20iOjAsInRvIjoxNSwic2VsZWN0ZWRGYWNldHMiOlt7ImtleSI6ImMiLCJ2YWx1ZSI6ImRlc2F5dW5vLXktbWVyaWVuZGEifSx7ImtleSI6ImMiLCJ2YWx1ZSI6ImF6dWNhci15LWVuZHVsemFudGVzIn0seyJrZXkiOiJjIiwidmFsdWUiOiJhenVjYXIifV0sImZhY2V0c0JlaGF2aW9yIjoiU3RhdGljIiwiY2F0ZWdvcnlUcmVlQmVoYXZpb3IiOiJkZWZhdWx0Iiwid2l0aEZhY2V0cyI6ZmFsc2UsInZhcmlhbnQiOiJudWxsLW51bGwiLCJhZHZlcnRpc2VtZW50T3B0aW9ucyI6eyJzaG93U3BvbnNvcmVkIjp0cnVlLCJzcG9uc29yZWRDb3VudCI6MywiYWR2ZXJ0aXNlbWVudFBsYWNlbWVudCI6InRvcF9zZWFyY2giLCJyZXBlYXRTcG9uc29yZWRQcm9kdWN0cyI6dHJ1ZX19%22%7D'
    
    # Encabezados (simula el navegador)
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 'VtexRCSessionIdv7=6e9d51a5-c74b-44c9-9971-b0bb8ba81dde; VtexRCMacIdv7=b09b54e3-c9ec-4d47-b552-e10c120cf012; _gcl_au=1.1.1492931608.1735305151; _gid=GA1.3.174540012.1735305151; __kdtv=t%3D1735305151397%3Bi%3D29924344dc044809a3213ead87a593f186e41744; _kdt=%7B%22t%22%3A1735305151397%2C%22i%22%3A%2229924344dc044809a3213ead87a593f186e41744%22%7D; VTEXSC=sc=1; ISSMB=ScreenMedia=0&UserAcceptMobile=False; SGTS=8915406B30546143C61DBAC54C4F3D27; CheckoutOrderFormOwnership=; vtex_segment=eyJjYW1wYWlnbnMiOm51bGwsImNoYW5uZWwiOiIxIiwicHJpY2VUYWJsZXMiOm51bGwsInJlZ2lvbklkIjpudWxsLCJ1dG1fY2FtcGFpZ24iOm51bGwsInV0bV9zb3VyY2UiOm51bGwsInV0bWlfY2FtcGFpZ24iOm51bGwsImN1cnJlbmN5Q29kZSI6IkFSUyIsImN1cnJlbmN5U3ltYm9sIjoiJCIsImNvdW50cnlDb2RlIjoiQVJHIiwiY3VsdHVyZUluZm8iOiJlcy1BUiIsImNoYW5uZWxQcml2YWN5IjoicHVibGljIn0; _fbp=fb.2.1735305151872.799355841648030922; vtex_session=eyJhbGciOiJFUzI1NiIsImtpZCI6IjgxODcwMTM5LWNmMTYtNGRiNi1hZGUzLWQ4NDY3ODgyYTMwYyIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50LmlkIjpbXSwiaWQiOiJiMzJlODcyYS0wM2E3LTRiY2QtYmNkNS00OTg2NTBmYWRjODIiLCJ2ZXJzaW9uIjoyLCJzdWIiOiJzZXNzaW9uIiwiYWNjb3VudCI6InNlc3Npb24iLCJleHAiOjE3MzU5OTYzNTEsImlhdCI6MTczNTMwNTE1MSwianRpIjoiODVjODQwOTItMDMxZi00YzViLTgwYmItZjc0NjM2MGFmNzgwIiwiaXNzIjoic2Vzc2lvbi9kYXRhLXNpZ25lciJ9.CP467FN9KUCLKvjI5ULnhZtIKfqU_52zfp78eM64m0t1bKrY0JiJY8HvtfAWMikleRqGp1oBKrgroCu_CjODFg; checkout.vtex.com=__ofid=1a68c780b971418db8416b6362253a0d; _gat_UA-125149805-1=1; _ga_NY76PB0BZ5=GS1.1.1735305151.1.1.1735305246.59.0.0; _ga=GA1.1.1972036693.1735305151; janus_sid=8e6ef8ce-a900-44ea-bbe1-d2301a538f6c',  # Coloca todas las cookies necesarias aquí
        'Host': 'www.cordiez.com.ar',
        'Referer': 'https://www.cordiez.com.ar/desayuno-y-merienda/azucar-y-edulcorante/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    
    response = requests.get(url)

    content_type = response.headers.get("Content-Type", "")
    print(f"Content-Type: {content_type}")

    # Si el contenido es JSON
    if "application/json" in content_type:
        try:
            # Parsear directamente como JSON
            data_json = response.json()
            print("Datos JSON cargados correctamente.")
        except json.JSONDecodeError as e:
            print(f"Error al cargar JSON: {e}")
            return pd.DataFrame()  # Retornar un DataFrame vacío en caso de error
    else:
        print("El contenido no es JSON. Aquí está el texto sin procesar:")
        print(response.text)
        return pd.DataFrame()
    
    productos_lista = []
    supermercado = 'CRF'

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        for producto in data_json:  # Iterar sobre la lista de productos
            nombre = producto.get('productName', 'Nombre no encontrado')
            marca = producto.get('brand', 'Marca no encontrada')
            for item in producto.get('items', []):  # Itera sobre cada elemento en 'items'
                for seller in item.get('sellers', []):  # Itera sobre cada vendedor en 'sellers'
                    precioBase = seller.get('commertialOffer', {}).get('PriceWithoutDiscount', None)
                    precioOferta = seller.get('commertialOffer', {}).get('Price', None)
                    productos_lista.append([supermercado, nombre, marca, precioBase, precioOferta])
        
        # Crear el DataFrame después de llenar la lista
        df = pd.DataFrame(productos_lista, columns=['Supermercado', 'Producto', 'Marca', 'Precio', 'Oferta'])
        return df
    
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return pd.DataFrame()
    
"""
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