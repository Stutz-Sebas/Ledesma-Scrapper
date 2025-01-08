import requests
import json
import pandas as pd

def dia():
    url1 = 'https://diaonline.supermercadosdia.com.ar/_v/segment/graphql/v1?workspace=master&maxAge=short&appsEtag=remove&domain=store&locale=es-AR&__bindingId=39bdf81c-0d1f-4400-9510-96377195dd22&operationName=productSearchV3&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%229177ba6f883473505dc99fcf2b679a6e270af6320a157f0798b92efeab98d5d3%22%2C%22sender%22%3A%22vtex.store-resources%400.x%22%2C%22provider%22%3A%22vtex.search-graphql%400.x%22%7D%2C%22variables%22%3A%22eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6dHJ1ZSwic2t1c0ZpbHRlciI6IkZJUlNUX0FWQUlMQUJMRSIsInNpbXVsYXRpb25CZWhhdmlvciI6ImRlZmF1bHQiLCJpbnN0YWxsbWVudENyaXRlcmlhIjoiTUFYX1dJVEhPVVRfSU5URVJFU1QiLCJwcm9kdWN0T3JpZ2luVnRleCI6dHJ1ZSwibWFwIjoiY2F0ZWdvcnktMSxjYXRlZ29yeS0yLGNhdGVnb3J5LTMsY2F0ZWdvcnktMyIsInF1ZXJ5IjoiZGVzYXl1bm8vaW5mdXNpb25lcy15LWVuZHVsemFudGVzL2F6dWNhci9lZHVsY29yYW50ZXMiLCJvcmRlckJ5IjoiT3JkZXJCeVNjb3JlREVTQyIsImZyb20iOjAsInRvIjoxNSwic2VsZWN0ZWRGYWNldHMiOlt7ImtleSI6ImNhdGVnb3J5LTEiLCJ2YWx1ZSI6ImRlc2F5dW5vIn0seyJrZXkiOiJjYXRlZ29yeS0yIiwidmFsdWUiOiJpbmZ1c2lvbmVzLXktZW5kdWx6YW50ZXMifSx7ImtleSI6ImNhdGVnb3J5LTMiLCJ2YWx1ZSI6ImF6dWNhciJ9LHsia2V5IjoiY2F0ZWdvcnktMyIsInZhbHVlIjoiZWR1bGNvcmFudGVzIn1dLCJzZWFyY2hTdGF0ZSI6bnVsbCwiZmFjZXRzQmVoYXZpb3IiOiJTdGF0aWMiLCJjYXRlZ29yeVRyZWVCZWhhdmlvciI6ImRlZmF1bHQiLCJ3aXRoRmFjZXRzIjpmYWxzZSwiYWR2ZXJ0aXNlbWVudE9wdGlvbnMiOnsic2hvd1Nwb25zb3JlZCI6dHJ1ZSwic3BvbnNvcmVkQ291bnQiOjMsImFkdmVydGlzZW1lbnRQbGFjZW1lbnQiOiJ0b3Bfc2VhcmNoIiwicmVwZWF0U3BvbnNvcmVkUHJvZHVjdHMiOnRydWV9fQ%3D%3D%22%7D'
    url2 = 'https://diaonline.supermercadosdia.com.ar/_v/segment/graphql/v1?workspace=master&maxAge=short&appsEtag=remove&domain=store&locale=es-AR&__bindingId=39bdf81c-0d1f-4400-9510-96377195dd22&operationName=productSearchV3&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%229177ba6f883473505dc99fcf2b679a6e270af6320a157f0798b92efeab98d5d3%22%2C%22sender%22%3A%22vtex.store-resources%400.x%22%2C%22provider%22%3A%22vtex.search-graphql%400.x%22%7D%2C%22variables%22%3A%22eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6dHJ1ZSwic2t1c0ZpbHRlciI6IkZJUlNUX0FWQUlMQUJMRSIsInNpbXVsYXRpb25CZWhhdmlvciI6ImRlZmF1bHQiLCJpbnN0YWxsbWVudENyaXRlcmlhIjoiTUFYX1dJVEhPVVRfSU5URVJFU1QiLCJwcm9kdWN0T3JpZ2luVnRleCI6dHJ1ZSwibWFwIjoiY2F0ZWdvcnktMSxjYXRlZ29yeS0yLGNhdGVnb3J5LTMsY2F0ZWdvcnktMyIsInF1ZXJ5IjoiZGVzYXl1bm8vaW5mdXNpb25lcy15LWVuZHVsemFudGVzL2F6dWNhci9lZHVsY29yYW50ZXMiLCJvcmRlckJ5IjoiT3JkZXJCeVNjb3JlREVTQyIsImZyb20iOjE2LCJ0byI6MzEsInNlbGVjdGVkRmFjZXRzIjpbeyJrZXkiOiJjYXRlZ29yeS0xIiwidmFsdWUiOiJkZXNheXVubyJ9LHsia2V5IjoiY2F0ZWdvcnktMiIsInZhbHVlIjoiaW5mdXNpb25lcy15LWVuZHVsemFudGVzIn0seyJrZXkiOiJjYXRlZ29yeS0zIiwidmFsdWUiOiJhenVjYXIifSx7ImtleSI6ImNhdGVnb3J5LTMiLCJ2YWx1ZSI6ImVkdWxjb3JhbnRlcyJ9XSwib3BlcmF0b3IiOiJhbmQiLCJmdXp6eSI6IjAiLCJzZWFyY2hTdGF0ZSI6bnVsbCwiZmFjZXRzQmVoYXZpb3IiOiJTdGF0aWMiLCJjYXRlZ29yeVRyZWVCZWhhdmlvciI6ImRlZmF1bHQiLCJ3aXRoRmFjZXRzIjpmYWxzZSwiYWR2ZXJ0aXNlbWVudE9wdGlvbnMiOnsic2hvd1Nwb25zb3JlZCI6dHJ1ZSwic3BvbnNvcmVkQ291bnQiOjMsImFkdmVydGlzZW1lbnRQbGFjZW1lbnQiOiJ0b3Bfc2VhcmNoIiwicmVwZWF0U3BvbnNvcmVkUHJvZHVjdHMiOnRydWV9fQ%3D%3D%22%7D'
    
    urls = [url1, url2]
    
    headers = {
        'accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'content-type': 'application/json',
        #'Cookie': r'VtexWorkspace=master%3A-; _dyjsession=ohfe18pfhwkh9dtgyuxqzbsgxh2bsant; dy_fs_page=www.carrefour.com.ar%2Fdesayuno-y-merienda%2Fazucar-y-endulzantes%2Fazucar; _dy_csc_ses=ohfe18pfhwkh9dtgyuxqzbsgxh2bsant; _gcl_au=1.1.646870679.1735829605; VtexRCSessionIdv7=12c0e1e9-29fd-49da-b100-a4d4fb664745; VtexRCMacIdv7=cb0d736d-0dc5-4f00-8eae-0c5a16b9f1cb; _fbp=fb.2.1735829605314.905617956923716393; vtex-search-session=17bdacdc35044ee0991b566760864d78; vtex-search-anonymous=549ec06c190b4db48bad64863b83b044; sp-variant=null-null; _gid=GA1.3.1380777512.1735829606; _clck=1m3cp57%7C2%7Cfs8%7C0%7C1828; vtex_binding_address=carrefourar.myvtex.com/; CheckoutOrderFormOwnership=; vtex_segment=eyJjYW1wYWlnbnMiOm51bGwsImNoYW5uZWwiOiIxIiwicHJpY2VUYWJsZXMiOm51bGwsInJlZ2lvbklkIjoiVTFjalkyRnljbVZtYjNWeVlYSXdNREF5TzJOaGNuSmxabTkxY21GeU1EZzVPUT09IiwidXRtX2NhbXBhaWduIjpudWxsLCJ1dG1fc291cmNlIjpudWxsLCJ1dG1pX2NhbXBhaWduIjpudWxsLCJjdXJyZW5jeUNvZGUiOiJBUlMiLCJjdXJyZW5jeVN5bWJvbCI6IiQiLCJjb3VudHJ5Q29kZSI6IkFSRyIsImN1bHR1cmVJbmZvIjoiZXMtQVIiLCJjaGFubmVsUHJpdmFjeSI6InB1YmxpYyJ9; _dycnst=dg; _dyid=3940649929088084088; _dycst=dk.w.c.ms.fst.; _dy_geo=AR.SA.AR_X.AR_X_C%C3%B3rdoba; _dy_df_geo=Argentina..C%C3%B3rdoba; _dy_cs_gcg=Dynamic%20Yield%20Experiences; _dy_cs_cookie_items=_dy_cs_gcg; intent_audience=low; OptanonAlertBoxClosed=2025-01-02T14:53:46.474Z; eupubconsent-v2=CQKopQPQKopQPAcABBENDgCgAAAAAAAAAChQAAAAAAAA.YAAAAAAAAAAA; _dyid_server=3940649929088084088; _dy_toffset=1; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Jan+02+2025+11%3A54%3A18+GMT-0300+(hora+est%C3%A1ndar+de+Argentina)&version=6.24.0&isIABGlobal=false&hosts=&consentId=4064e2f1-dfbe-4305-8188-08651e53314b&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A0%2CC0039%3A0%2CC0023%3A0%2CC0056%3A0%2CC0005%3A0%2CSTACK1%3A0%2CSTACK42%3A0%2CC0069%3A0&geolocation=AR%3BX&AwaitingReconsent=false; _gat_UA-16760871-10=1; checkout.vtex.com=__ofid=5e3b98c913214bb78e2f169b84c668e7; _clsk=1stdjze%7C1735831171791%7C4%7C1%7Cv.clarity.ms%2Fcollect; janus_sid=1318fa18-a839-45b2-90fb-d3a7499b6c61; _dy_soct=1735831185!1594828.-37'1598112.-1561'1792788.-39'2288309.-37!ohfe18pfhwkh9dtgyuxqzbsgxh2bsant~1460764.-1561; _ga=GA1.1.1566035237.1735829605; _ga_YL72LN8HLQ=GS1.1.1735829605.1.1.1735831186.20.0.0; vtex_session=eyJhbGciOiJFUzI1NiIsImtpZCI6ImE2OTBhMmM1LTliZmMtNGJiNi05MjZlLTk0Njc1MzVhZWM2ZiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50LmlkIjpbXSwiaWQiOiIxMWI3MWFkOS03MWIxLTQxYTEtOWFkZS05YWVkMjVkNjBmODMiLCJ2ZXJzaW9uIjo1LCJzdWIiOiJzZXNzaW9uIiwiYWNjb3VudCI6InNlc3Npb24iLCJleHAiOjE3MzY1MjIzODcsImlhdCI6MTczNTgzMTE4NywianRpIjoiMWIzYTdiM2YtZTNjYS00NzJmLWI5NWMtZTBiODEyZWI3ZmQ4IiwiaXNzIjoic2Vzc2lvbi9kYXRhLXNpZ25lciJ9.Q8Icmjt6-7pCYXVYNEAZGUN7QckNP7uA4GdNeogimqqvoYEsnXkTLKQwwb4CzE65NMuTGChlTBn37zWgjTBVwg',
        'Host': 'diaonline.supermercadosdia.com.ar',
        'Referer': 'https://diaonline.supermercadosdia.com.ar/desayuno/infusiones-y-endulzantes/azucar',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    }

    productos_lista = []
    supermercado = 'DIA'
    
    for url in urls:
        
        # Solicitud HTTP
        try:
            response = requests.get(url)
            response.raise_for_status() # Lanzar excepción si el servidor devuelve un error
        except requests.RequestException as e:
            print(f"Error al conectar con {url}: {e}")
            continue

        # Verificar si el contenido es JSON
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            print(f"El contenido de {url} no es JSON. Se omite.")
            continue

        # Cargar el JSON
        try:
            data_json = response.json()
            print("Datos JSON cargados correctamente.")
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON de {url}: {e}")
            continue

        # Procesar productos si la respuesta es válida
        productos = data_json.get('data', {}).get('productSearch', {}).get('products', [])
        for producto in productos:
            nombre = producto.get('productName', 'Nombre no encontrado')
            marca = producto.get('brand', 'Marca no encontrada')
            precioBase = producto.get('priceRange', {}).get('listPrice', {}).get('highPrice', 0)

            item = producto.get('items', [{}])[0]
            sellers = item.get('sellers', [{}])[0]
            commertialOffer = sellers.get('commertialOffer', {})
            discountHighlights = commertialOffer.get('discountHighlights', [])

            if not discountHighlights:
                precioOferta = 0
                tipoOferta = 'Sin oferta'
            else:
                oferta = discountHighlights[0]
                precioOferta = producto.get('priceRange', {}).get('sellingPrice', {}).get('highPrice', 0)
                tipoOferta = oferta.get('name', 'Tipo de oferta no encontrado')

            productos_lista.append([supermercado, nombre, marca, precioBase, precioOferta, tipoOferta])

    # Crear DataFrame solo después de procesar todas las URLs
    df = pd.DataFrame(productos_lista, columns=['Supermercado', 'Producto', 'Marca', 'Precio', 'Oferta', 'Tipo de Oferta'])
    return df
    
data = dia()

print(data)