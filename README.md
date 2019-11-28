--levee on ubuntu

--airflow

sudo AIRFLOW_GPL_UNIDECODE=yes pip install "apache-airflow[celery, crypto, postgres, hive, rabbitmq, redis]"

--postgres

sudo apt-get install postgresql postgresql-contrib
sudo /etc/init.d/postgresql start

--user

sudo adduser airflow
sudo usermod -aG sudo airflow
su - airflow
sudo -u postgres psql

--put in the user profile

export AIRFLOW_HOME=~/airflow

--metadata

CREATE USER airflow PASSWORD 'airflow';
CREATE DATABASE airflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
\du

--testing

psql -d airflow
\conninfo

--change db to postgres

vim airflow/airflow.cfg

executor = LocalExecutor
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@localhost:5432/airflow
airflow initdb

--airflow

airflow initdb
airflow upgradedb
airflow webserver -p 8080 &
airflow scheduler &

--aws

sudo apt-get install awscli
sudo pip install boto3
pip install awscli 

aws configure

AKIAIOSFODNN7EXAMPLE
wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
us-east-1
json

--run the dag without the file in bucket

--run the dag with the file in bucket
