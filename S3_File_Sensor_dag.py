from airflow import DAG
from airflow.operators import SimpleHttpOperator, HttpSensor, BashOperator, EmailOperator, S3KeySensor
from datetime import datetime, timedelta

default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2019, 11, 27),
        'email': ['brunoof1@hotmail.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 5,
        'retry_delay': timedelta(minutes=5)
}

with DAG('S3_File_Sensor_dag.py',
        default_args=default_args,
        schedule_interval= '@once') as dag:

        t1 = BashOperator(task_id='bash_task', bash_command='echo "hello world" > s3_conn_test.txt', dag=dag)

        sensor = S3KeySensor(task_id='S3Key_task', bucket_key='AirflowLogs/teste.txt', wildcard_match=True, bucket_name='levee-datalake', s3_conn_id='s3_default', timeout=18*60*60, poke_interval=120, dag=dag)

        t1.set_upstream(sensor)