                                        Installation steps on UBUNTU

					Airflow

sudo AIRFLOW_GPL_UNIDECODE=yes pip install "apache-airflow[celery, crypto, postgres, hive, rabbitmq, redis]"

					Postgres

sudo apt-get install postgresql postgresql-contrib
sudo /etc/init.d/postgresql start

					SO User

sudo adduser airflow
sudo usermod -aG sudo airflow
su - airflow
sudo -u postgres psql

					User profile

export AIRFLOW_HOME=~/airflow

					Postgres Objects

CREATE USER airflow PASSWORD 'airflow';
CREATE DATABASE airflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
\du

					Postgres Testing

psql -d airflow
\conninfo

					Change airflow db to postgres

vim airflow/airflow.cfg

executor = LocalExecutor
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@localhost:5432/airflow
airflow initdb

					Starting Airflow DB and process

airflow initdb
airflow upgradedb
airflow webserver -p 8080 &
airflow scheduler &

					Install AWS requirements

sudo apt-get install awscli
sudo pip install boto3
pip install awscli 

					Configure AWS credentials

aws configure

AKIAIOSFODNN7EXAMPLE
wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
us-east-1
json

Run the dag without the file in bucket

Run the dag with the file in bucket
