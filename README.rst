Chartly
=======

.. image:: https://circleci.com/gh/dataglu/chartly/tree/master.svg?style=svg
    :target: https://circleci.com/gh/dataglu/chartly/tree/master

.. image:: https://codecov.io/github/dataglu/chartly/coverage.svg?token=LQPKDYzyKr&branch=master
    :target: https://codecov.io/github/dataglu/chartly?branch=master

Requirements
------------

This project requires Python 2.7 and MySQL:

.. code-block:: bash

    $ sudo apt-get install mysql-server libmysqlclient-dev python-dev libblas-dev liblapack-dev gfortran


Installation
------------

Install Python dependencies (in a virtualenv preferably):

.. code-block:: bash

    $ pip install -r requirements/local.txt


Setup the Database
------------------

Create the databases and user permissions::

    CREATE DATABASE django CHARACTER SET utf8 COLLATE utf8_general_ci;
    GRANT ALL PRIVILEGES ON django.*  TO 'django'@'localhost' IDENTIFIED BY 'django';
    CREATE DATABASE test CHARACTER SET utf8 COLLATE utf8_general_ci;
    GRANT ALL PRIVILEGES ON test.*  TO 'django'@'localhost' IDENTIFIED BY 'django';


Database Migrations
-------------------

To initialize or update the database:

.. code-block:: bash

    ./manage.py migrate

To create a new super user:

.. code-block:: bash

    ./manage.py createsuperuser


Running the Server
------------------

To start the Django server on port 7878:

.. code-block:: bash

    $ ./manage.py runserver 7878

Now visit http://localhost:7878/ in your browser.
