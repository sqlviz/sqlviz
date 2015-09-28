#!/bin/bash

sudo apt-get install libmysqlclient-dev python-dev libblas-dev liblapack-dev gfortran lamp-server^ python-pip python-numpy python-psycopg2  python-psycopg2 libpq-dev libfreetype6-dev libxft-dev phantomjs libxml2-dev libxslt1-dev unzip openjdk-7-jre-headless
echo 'apt get complete'
sudo pip install -r requirements/local.txt
echo 'pip install complete'

# Create passwords randomly

MYSQLPWD=$(openssl rand -hex 32)
DJANGOPWD=$(openssl rand -hex 32)
PWD_JSON='{
    "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY": "OATHKEY",
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET" : "OATHSECRET",
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
sed -i "s@MYSQLPWD@$MYSQLPWD@" initial_data/initial_data.json

echo 'please provide OATH KEY'
read OATHKEY
echo 'please provide OATHSECRET'
read OATHSECRET

sed -i "s@OATHKEY@$OATHKEY@" initial_data/initial_data.json
sed -i "s@OATHSECRET@$OATHSECRET@" initial_data/initial_data.json

echo 'please provide mysql root password'

mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS django CHARACTER SET utf8 COLLATE utf8_general_ci;
	GRANT ALL PRIVILEGES ON django.*  TO 'django'@'localhost' IDENTIFIED BY '$MYSQLPWD';
	CREATE DATABASE IF NOT EXISTS scratch CHARACTER SET utf8 COLLATE utf8_general_ci;
	GRANT ALL PRIVILEGES ON scratch.*  TO 'django'@'localhost' IDENTIFIED BY '$MYSQLPWD';
  CREATE DATABASE IF NOT EXISTS django_test CHARACTER SET utf8 COLLATE utf8_general_ci;
	GRANT ALL PRIVILEGES ON django_test.*  TO 'django'@'localhost' IDENTIFIED BY '$MYSQLPWD';"

echo 'begin django migrations'
./manage.py migrate

./manage.py createsuperuser

./manage.py crontab add

rm -rf fieldkeys
mkdir fieldkeys
keyczart create --location=fieldkeys --purpose=crypt
keyczart addkey --location=fieldkeys --status=primary --size=256

echo 'cloning highcharts. please see licensing details'
git clone https://github.com/highslide-software/highcharts.com.git website/static/Highcharts
git clone https://github.com/highslide-software/highmaps-release.git website/static/Highmaps

echo 'loading data into database'
python manage.py loaddata initial_data/djia_data.json
python manage.py loaddata initial_data/initial_data.json

chmod  -R 777 media

echo 'installing elastic search'
wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.7.2.zip
sudo unzip elasticsearch-1.7.2 -d /usr/local/elasticsearch
rm elasticsearch-1.7.2.zip
cd /usr/local/elasticsearch/elasticsearch-1.7.2/

.bin/elasticsearch -d

echo 'starting dev server'
./manage.py runserver 0.0.0.0:8000
