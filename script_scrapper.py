import json
import requests
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

# Función auxiliar para buscar un elemento
def buscar_elemento(contenedor, etiqueta, es_clase, id_clase):
    try:
        if es_clase:
            elemento = contenedor.find(etiqueta, class_=id_clase)
        else:
            elemento = contenedor.find(etiqueta, id=id_clase)
        
        if elemento is None:
            print(f"No se encontró el elemento: {etiqueta} con {'class' if es_clase else 'id'}={id_clase}")
        return elemento
    except Exception as e:
        print(f"Error buscando elemento: {e}")
        return None

# Función auxiliar para buscar múltiples elementos
def buscar_elementos(contenedor, etiqueta, es_clase, id_clase):
    try:
        if es_clase:
            return contenedor.find_all(etiqueta, class_=id_clase)
        return contenedor.find_all(etiqueta, id=id_clase)
    except Exception as e:
        print(f"Error buscando elementos: {e}")
        return []

# Función para extraer el precio
def extraer_precio(elemento):
    try:
        if elemento:
            precio_texto = elemento.get_text(strip=True).replace(u'\xa0', u' ')
            precio = float(precio_texto.replace('$', '').replace('.', '').replace(',', '.').strip())
            return precio
        return np.nan
    except ValueError as e:
        print(f"Error extrayendo precio: {e}")
        return np.nan
    
# Función principal para procesar un supermercado
def supermercado(params):
    try:
        url = params["url"]
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        contenedor = buscar_elemento(soup, params["etiqueta_cont"], params["es_clase_cont"], params["id_class_cont"])
        if not contenedor:
            print(f"No se encontró el contenedor para {params['nombre']}")
            return []

        productos = buscar_elementos(contenedor, params["etiqueta_prod"], params["es_clase_prod"], params["id_class_prod"])
        productos_lista = []

        for producto in productos:
            try:
                nombre = buscar_elemento(producto, params["etiqueta_nombre"], params["es_clase_nombre"], params["id_class_nombre"])
                articulo = nombre.get_text(strip=True) if nombre else 'Nombre no encontrado'

                precio_lista = buscar_elemento(producto, params["etiqueta_precio"], params["es_clase_precio"], params["id_class_precio"])
                precio_oferta = buscar_elemento(producto, params["etiqueta_oferta"], params["es_clase_oferta"], params["id_class_oferta"])

                precio_lista = extraer_precio(precio_lista)
                precio_oferta = extraer_precio(precio_oferta)

                if np.isnan(precio_lista):
                    precio_lista = precio_oferta
                    precio_oferta = np.nan

                productos_lista.append([params["nombre"], articulo, precio_lista, precio_oferta])
            except Exception as e:
                print(f"Error procesando producto: {e}")
                continue

        print(f"Productos extraídos de {params['nombre']}: {len(productos_lista)}")
        return productos_lista
    except Exception as e:
        print(f"Error procesando supermercado {params['nombre']}: {e}")
        return []

# Cargar datos del archivo JSON
def cargar_supermercados(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            supermercados = json.load(file)

        todos_los_productos = []
        for params in supermercados:
            productos = supermercado(params)
            todos_los_productos.extend(productos)

        return todos_los_productos
    except FileNotFoundError:
        print("Error: El archivo JSON no se encontró.")
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el archivo JSON: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

    return []

# Función main
def main():
    try:
        archivo = 'Estructura_Con_Precio_Oferta_0.csv'
        df_plantilla = pd.read_csv(archivo, header=[0, 1, 2], index_col=[0, 1], encoding='utf-8')

        productos_scrapeados = cargar_supermercados('supermercados.json')

        df_productos_scrapeados = pd.DataFrame(productos_scrapeados, columns=['Supermercado', 'Producto', 'Precio Lista', 'Precio Oferta'])
        df_productos_scrapeados.to_csv('Prueba.csv')

        #cargar_precios_en_planilla(df_plantilla, df_productos_scrapeados)

        print("Proceso completado exitosamente.")
        print(f"Productos scrapeados\n: {df_productos_scrapeados}")
        return df_plantilla, df_productos_scrapeados
    except Exception as e:
        print(f"Error en la función main: {e}")

