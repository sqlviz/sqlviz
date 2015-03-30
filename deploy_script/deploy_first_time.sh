sudo yum install mysql-server libmysqlclient-dev python-dev libblas-dev liblapack-dev gfortran

pip install -r requirements/base.txt
pip install -r requirements/local.txt

mysql -u root

CREATE DATABASE IF NOT EXISTS django CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON django.*  TO 'django'@'localhost' IDENTIFIED BY 'django';
CREATE DATABASE IF NOT EXISTS scratch CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON scratch.*  TO 'django'@'localhost' IDENTIFIED BY 'django';


CREATE DATABASE IF NOT EXISTS test CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON test.*  TO 'django'@'localhost' IDENTIFIED BY 'django';

quit;

./manage.py migrate

./manage.py createsuperuser

mkdir fieldkeys
keyczart create --location=fieldkeys --purpose=crypt
keyczart addkey --location=fieldkeys --status=primary --size=256

./manage.py runserver 7878    

chmod  -R 777 media
