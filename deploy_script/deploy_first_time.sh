#!/bin/bash

sudo apt-get install libmysqlclient-dev python-dev libblas-dev liblapack-dev gfortran lamp-server^ python-pip python-numpy python-psycopg2  python-psycopg2 libpq-dev libfreetype6-dev libxft-dev phantomjs libxml2-dev libxslt1-dev

sudo pip install -r requirements/local.txt

mysql -u root

CREATE DATABASE IF NOT EXISTS django CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON django.*  TO 'django'@'localhost' IDENTIFIED BY 'django';
CREATE DATABASE IF NOT EXISTS scratch CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON scratch.*  TO 'django'@'localhost' IDENTIFIED BY 'django';

quit;

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


