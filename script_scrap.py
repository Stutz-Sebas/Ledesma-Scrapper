import requests
import pandas as pd
import json

def obtener_valor(diccionario, camino):
    valor = diccionario
    try:
        for paso in camino:
            if isinstance(paso, int):
                if isinstance(valor, list) and len(valor) > paso:
                    valor = valor[paso]
                else:
                    return None
            else:
                valor = valor.get(paso, {})
        return valor
    except (IndexError, AttributeError):
        return None

def cargar_datos(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

    productos_lista = []

    for supermercado, detalles in config.items():
        urls = detalles.get("urls", [])
        print(f"Procesando {supermercado}...")
        
        estructura = detalles.get("estructura", {})
        print(f"Estructura de datos: {estructura}")

        if not urls:
            print(f"No hay URLs definidas para {supermercado}.")
            continue

        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    data_json = response.json()
                    productos = data_json if isinstance(data_json, list) else data_json.get('products', [])
                    
                    for producto in productos:
                        nombre = obtener_valor(producto, estructura.get("productName", [])) or "Nombre no encontrado"
                        marca = obtener_valor(producto, estructura.get("brand", [])) or "Marca no encontrada"
                        precio_base = obtener_valor(producto, estructura.get("listPrice", [])) or 0
                        precio_oferta = obtener_valor(producto, estructura.get("sellingPrice", [])) or 0
                        tipo_oferta = obtener_valor(producto, estructura.get("discountHighlights", [])) or "Sin oferta"
                        
                        productos_lista.append([supermercado, nombre, marca, precio_base, precio_oferta, tipo_oferta])
                except json.JSONDecodeError:
                    print(f"Error al decodificar JSON desde {url}")
            else:
                print(f"Error en la solicitud a {url}: {response.status_code}")
    
    df = pd.DataFrame(productos_lista, columns=["Supermercado", "Producto", "Marca", "Precio Base", "Precio Oferta", "Tipo de Oferta"])
    print(df)
    return df

try:
    df = cargar_datos("config.json")
    df.to_csv("productos_supermercados.csv", index=False)
    print("Datos guardados en 'productos_supermercados.csv'")
except KeyError as e:
    print(f"Error: {e}")