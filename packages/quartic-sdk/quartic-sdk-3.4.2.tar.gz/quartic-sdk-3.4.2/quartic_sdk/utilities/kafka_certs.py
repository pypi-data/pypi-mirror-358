import logging
import requests

from quartic_sdk import GraphqlClient


def download_kafka_certs(client: GraphqlClient, path_to_save: str):
    QUERY = """
             query KafkaCerts {
                            kafkaCerts
                            }
            """
    try:
        file_path = client.execute_query(QUERY)['data']['kafkaCerts']['file_path']
        res = requests.get(f'{client._get_graphql_url()}utils/media_download',
                           headers={'Authorization': f'Bearer {client.access_token}'},
                           params={'file_path': file_path},
                           )
        certs_path = f"{path_to_save}/kafka_certs.zip"
        with open(certs_path, 'wb') as file:
            file.write(res.content)
        logging.info(f"Successfully Downloaded files to : {certs_path}")
    except Exception as e:
        logging.info(f"Error occurred while downloading kafka-certs")