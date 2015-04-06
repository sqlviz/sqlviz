#!/bin/bash

sudo apt-get install mysql-server libmysqlclient-dev python-dev libblas-dev liblapack-dev gfortran lamp-server^ python-pip python-numpy python-psycopg2  python-psycopg2 libpq-dev libfreetype6-dev libxft-dev phantomjs libxml2-dev libxslt1-dev

pip install -r requirements/local.txt


## Create passwords randomly

MYSQLPWD=$(openssl rand -base64 32)
DJANGOPWD=$(openssl rand -base64 32)
PWD_JSON='{
    "SECRET_KEY" : "DJANGOPWD",
    "EMAIL": {
        "EMAIL_HOST" : "smtp.gmail.com",
        "EMAIL_HOST_PASSWORD" : "",
        "EMAIL_HOST_USER" : "test@example.com",
        "EMAIL_PORT" : 587,
        "EMAIL_USE_TLS" : true
    },
    "DJANGO" : {
        "DB_TYPE" : "mysql",
        "USER" : "django",
        "PWD" : "MYSQLPWD",
        "HOST" : "localhost",
        "PORT" : 3306,
        "DB" : "django"
    },
    "SCRATCH" : {
        "DB_TYPE" : "mysql",
        "USER" : "django",
        "PWD" : "MYSQLPWD",
        "HOST" : "localhost",
        "PORT" : 3306,
        "DB" : "scratch"
    }
}'

PWD_JSON="${PWD_JSON//DJANGOPWD/$DJANGOPWD}"
PWD_JSON="${PWD_JSON//MYSQLPWD/$MYSQLPWD}"

# Place passwords in necassary files
echo "$PWD_JSON" > sqlviz/passwords.json

mysql -u root -e "CREATE DATABASE IF NOT EXISTS django CHARACTER SET utf8 COLLATE utf8_general_ci;
	GRANT ALL PRIVILEGES ON django.*  TO 'django'@'localhost' IDENTIFIED BY '$MYSQLPWD';
	CREATE DATABASE IF NOT EXISTS scratch CHARACTER SET utf8 COLLATE utf8_general_ci;
	GRANT ALL PRIVILEGES ON scratch.*  TO 'django'@'localhost' IDENTIFIED BY '$MYSQLPWD';"

# Modify  Initial Data to include MySQL Password
sed -i "s@MYSQLPWD@$MYSQLPWD@" initial_data/initial_data.json

./manage.py migrate

./manage.py createsuperuser

git clone https://github.com/highslide-software/highcharts.com.git website/static/Highcharts
git clone https://github.com/highslide-software/highmaps-release.git website/static/Highmaps

rm -rf fieldkeys
mkdir fieldkeys
keyczart create --location=fieldkeys --purpose=crypt
keyczart addkey --location=fieldkeys --status=primary --size=256

python manage.py loaddata initial_data/djia_data.json
python manage.py loaddata initial_data/initial_data.json

chmod  -R 777 media

./manage.py runserver 7878    


