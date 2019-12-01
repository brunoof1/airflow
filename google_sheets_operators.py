import logging
import boa
import datetime
import os
import json
import time
import gzip

from airflow.models import BaseOperator, Variable
from hooks.google.google_sheets_hook import GoogleSheetsHook
from airflow.hooks.base_hook import BaseHook
from airflow.hooks.S3_hook import S3Hook
from airflow.plugins_manager import AirflowPlugin


class GoogleSheetsToS3Operator(BaseOperator):

    def __init__(self,
                 google_conn_id,
                 sheet_id,
                 s3_conn_id,
                 s3_key,
                 s3_bucket_name,
                 compression_bound,
                 include_schema=False,
                 sheet_names=[],
                 range=None,
                 output_format='json',
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.google_conn_id = google_conn_id
        self.sheet_id = sheet_id
        self.sheet_names = sheet_names
        self.s3_conn_id = s3_conn_id
        self.s3_key = s3_key
        self.s3_bucket_name = s3_bucket_name
        self.include_schema = include_schema
        self.range = range
        self.output_format = output_format.lower()
        self.compression_bound = compression_bound

    def execute(self, context):
        g_conn = GoogleSheetsHook(self.google_conn_id)

        sheet_names = self.sheet_names

        sheets_object = g_conn.get_service_object('sheets', 'v4')
        logging.info('Retrieved Sheets Object')

        response = sheets_object.spreadsheets().get(spreadsheetId=self.sheet_id,
                                                    includeGridData=True).execute()

        title = response.get('properties').get('title')
        sheets = response.get('sheets')

        final_output = dict()

        total_sheets = []
        for sheet in sheets:
            name = sheet.get('properties').get('title')
            name = boa.constrict(name)
            total_sheets.append(name)

            if self.sheet_names:
                if name not in sheet_names:
                    logging.info('{} is not found in available sheet names.'.format(name))
                    continue

            table_name = name
            data = sheet.get('data')[0].get('rowData')
            output = []

            for row in data:
                row_data = []
                values = row.get('values')
                for value in values:
                    ev = value.get('effectiveValue')
                    if ev is None:
                        row_data.append(None)
                    else:
                        for v in ev.values():
                            row_data.append(v)

                output.append(row_data)

            if self.output_format == 'json':
                headers = output.pop(0)
                output = [dict(zip(headers, row)) for row in output]

            final_output[table_name] = output

        s3 = S3Hook(self.s3_conn_id)

        for sheet in final_output:
            output_data = final_output.get(sheet)

            file_name, file_extension = os.path.splitext(self.s3_key)

            output_name = ''.join([file_name, '_', sheet, file_extension])

            if self.include_schema is True:
                schema_name = ''.join([file_name, '_', sheet, '_schema', file_extension])
            else:
                schema_name=None

            self.output_manager(s3, output_name, output_data, context, sheet, schema_name)

        dag_id = context['ti'].dag_id

        var_key = '_'.join([dag_id, self.sheet_id])
        Variable.set(key=var_key, value=json.dumps(total_sheets))

        time.sleep(10)

        return boa.constrict(title)

    def output_manager(self, s3, output_name, output_data, context, sheet_name, schema_name=None):
        if self.output_format == 'json':
            output = '\n'.join([json.dumps({boa.constrict(str(k)): v
                                            for k, v in record.items()})
                                for record in output_data])

            enco_output = str.encode(output, 'utf-8')

            if len(enco_output) / 1024 / 1024 < self.compression_bound:
                logging.info("File is more than {}MB, gzip compression will be applied".format(self.compression_bound))
                gzip_output = gzip.compress(enco_output, compresslevel=5)
                self.xcom_push(context, key='is_compressed_{}'.format(sheet_name), value="compressed")
                #TODO Finish the decision make if compressed or not
                s3.load_bytes(bytes_data=enco_output, key=self.s3_key+'.json', bucket_name=self.s3_bucket_name, replace=True)
                s3.load_bytes(bytes_data=gzip_output, key=self.s3_key+'.gz', bucket_name=self.s3_bucket_name, replace=True)


class GoogleSheetsToS3OperatorPlugin(AirflowPlugin):
    name = "google_sheets_to_s3_operator"
    operators = [GoogleSheetsToS3Operator]
