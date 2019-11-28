import os
from pprint import pprint
from googleapiclient import discovery

from oauth2client.service_account import ServiceAccountCredentials

from airflow.hooks.base_hook import BaseHook
from airflow.plugins_manager import AirflowPlugin

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/airflow/airflow/credentials.json'

class GoogleSheetsHook(BaseHook):
    def __init__(self, google_conn_id='google_default'):
        self.connection = self.get_connection(google_conn_id)
        print('DEBUG 1' ,self.connection)

    def get_service_object(self,
                           api_name,
                           api_version,
                           scopes=None):

        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is not None:
            credentials = None
            print('DEBUG 3', api_name, api_version, credentials)

        return discovery.build(api_name, api_version, credentials=credentials, cache_discovery=False)


class GoogleSheetsHookPlugin(AirflowPlugin):
    name = "google_sheets_hook"
    hooks = [GoogleSheetsHook]
