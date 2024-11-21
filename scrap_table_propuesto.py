import requests
from bs4 import BeautifulSoup
import uuid
import boto3

def handler_procesar(event, context):
    url_api = "https://ultimosismo.igp.gob.pe/api/ultimo-sismo/ajaxb/2024"
    respuesta = requests.get(url_api)
    
    if respuesta.status_code != 200:
        return {
            'codigo_estado': respuesta.status_code,
            'mensaje': 'Error al acceder a la API del sitio web'
        }
        
    lista_sismos = []
    datos_json = respuesta.json()
    resultados_ordenados = []
    lista_temporal = []

    for elemento in datos_json:
        lista_sismos.append((elemento["createdAt"], elemento))
    
    lista_sismos.sort(key=lambda item: item[0], reverse=True)
    
    for indice in range(50):
        lista_temporal.append(lista_sismos[indice])
    
    recurso_dynamodb = boto3.resource('dynamodb')
    tabla_dynamodb = recurso_dynamodb.Table('TablaWebScrapingModificada')
    
    datos_existentes = tabla_dynamodb.scan()
    with tabla_dynamodb.batch_writer() as escritor:
        for registro in datos_existentes['Items']:
            escritor.delete_item(Key={'id': registro['id']})
    
    contador = 1
    for fila in lista_temporal:
        informacion = fila[1]
        informacion['numero'] = contador
        informacion['id'] = str(uuid.uuid4())
        resultados_ordenados.append(informacion)
        tabla_dynamodb.put_item(Item=informacion)
        contador += 1
    
    return {
        'codigo_estado': 200,
        'resultados': resultados_ordenados
    }
