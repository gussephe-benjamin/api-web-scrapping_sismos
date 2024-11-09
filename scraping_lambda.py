import json
import requests
from bs4 import BeautifulSoup
import boto3
from uuid import uuid4

# Inicializar el recurso de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = "TablaScrapingDynamoDBNueva"  # Nombre actualizado para la nueva tabla DynamoDB

def lambda_handler(event, context):
    url = "https://ejemplo.com"  # Cambia esto a la URL que deseas scrapear

    try:
        # 1. Realizar la solicitud HTTP GET
        response = requests.get(url)
        response.raise_for_status()

        # 2. Parsear el contenido HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # 3. Encontrar todas las tablas en la página
        tables = soup.find_all("table")

        # Conectarse a la tabla DynamoDB
        table = dynamodb.Table(table_name)

        # Iterar sobre cada tabla encontrada
        for i, table_html in enumerate(tables):
            rows = table_html.find_all("tr")
            
            for row in rows:
                # Extraer celdas
                cells = row.find_all(["td", "th"])
                cell_data = [cell.text.strip() for cell in cells]
                
                # Crear item para DynamoDB
                item = {
                    "id": str(uuid4()),  # Generar un ID único para cada fila
                    "table_number": i,   # Número de tabla (si hay más de una en la página)
                    "row_data": cell_data  # Datos de la fila
                }

                # Guardar el item en DynamoDB
                table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps({"message": "Datos almacenados en TablaScrapingDynamoDBNueva exitosamente"})
        }

    except requests.RequestException as e:
        # Manejo de errores en caso de fallo de la solicitud
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
