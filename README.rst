SQLViz
=======

.. image:: https://circleci.com/gh/sqlviz/sqlviz/tree/master.svg?style=svg&circle-token=c5003ccfe0b8fbf630da12aeef19e81eb39efcca
    :target: https://circleci.com/gh/sqlviz/sqlviz/tree/master

.. image:: https://codecov.io/github/sqlviz/sqlviz/coverage.svg?token=LQPKDYzyKr&branch=master
    :target: https://codecov.io/github/sqlviz/sqlviz?branch=master

SQLViz is a data visualization platform built on Django

Requirements
------------

This project requires Python 2.7, MySQL, and Postgres.  Instructions below are for Ubuntu.  These instructions have been tested on an EC2 "Ubuntu Server 14.04 LTS (HVM), SSD Volume Type - ami-29ebb519" server.

Installation
------------

Install required Linux packages.  

.. code-block:: bash

    $ sudo apt-get install mysql-server libmysqlclient-dev python-dev libblas-dev liblapack-dev gfortran lamp-server^ python-pip python-numpy python-psycopg2  python-psycopg2 libpq-dev libfreetype6-dev libxft-dev phantomjs libxml2-dev libxslt1-dev


Install Python dependencies (in a virtualenv preferably):

.. code-block:: bash

    $ pip install -r requirements/local.txt


Setup the Database
------------------

Create the databases and user permissions::

    CREATE DATABASE IF NOT EXISTS django CHARACTER SET utf8 COLLATE utf8_general_ci;
    GRANT ALL PRIVILEGES ON django.*  TO 'django'@'localhost' IDENTIFIED BY 'django';
    CREATE DATABASE IF NOT EXISTS scratch CHARACTER SET utf8 COLLATE utf8_general_ci;
    GRANT ALL PRIVILEGES ON scratch.*  TO 'django'@'localhost' IDENTIFIED BY 'django';

Database Migrations
-------------------

To initialize or update the database:

.. code-block:: bash

    ./manage.py migrate

To create a new super user and enter credentials for that user:

.. code-block:: bash

    ./manage.py createsuperuser


Running the Server
------------------

To start the Django server on port 7878:

.. code-block:: bash

    $ ./manage.py runserver 0.0.0.0:7878

Now visit http://localhost:7878/ in your browser, or the IP the server is running from.

Licensing
---------
* Highcharts licensing is required for Highcharts and Highmaps (each are separate).
    * http://shop.highsoft.com/highcharts.html
* Once license has been acquired, place Highcharts into the necassary folder.
.. code-block:: bash
    
    $ git clone https://github.com/highslide-software/highcharts.com.git website/static/Highcharts
    $ git clone https://github.com/highslide-software/highmaps-release.git website/static/Highmaps

Loading Initial Data
--------------------

Load data into to SQLViz so there is out of gate functionality

.. code-block:: bash

    $ python manage.py loaddata initial_data/djia_data.json 
    $ python manage.py loaddata initial_data/initial_data.json 
    

Enabling Cron
-------------

Execute to set up script to run reporting:

.. code-block:: bash

    $ python manage.py crontab add


Keyset for Encryption Fields
----------------------------

Create Django encrypted keys:

.. code-block:: bash

    $ rm -rf fieldkeys
    $ mkdir fieldkeys
    $ keyczart create --location=fieldkeys --purpose=crypt
    $ keyczart addkey --location=fieldkeys --status=primary --size=256

Enable Uploads
--------------

If running with Apache, you may need to grant access to media folder and the debug.log file

.. code-block:: bash

    $ chmod  -R 777 media
    $ chmod 777 debug.log


* First repo is fairly large.  You can checkout the alternative highcharts release branch into the js folder and also checking out the export branch separately.
* SQLViz does NOT include any warranty for the licenses of used software. 

Passwords
---------

* You can set up a passwords.json file in the sqlviz folder.  It is in the gitignore to avoid copy-ing passwords into a repo.  Email is used for automated reporting.
.. code-block:: javascript

    {
        "SECRET_KEY" : "",
        "EMAIL": {
            "EMAIL_HOST" : "smtp.gmail.com",
            "EMAIL_HOST_PASSWORD" : "",
            "EMAIL_HOST_USER" : "",
            "EMAIL_PORT" : 587,
            "EMAIL_USE_TLS" : true
        },
        "DJANGO" : {
            "DB_TYPE" : "",
            "USER" : "",
            "PWD" : "",
            "HOST" : "",
            "PORT" : "",
            "DB" : ""
        },
        "SCRATCH" : {
            "DB_TYPE" : "",
            "USER" : "",
            "PWD" : "",
            "HOST" : "",
            "PORT" : "",
            "DB" : ""
        }
    }


Using SQLViz
------------

Setting up a database
~~~~~~~~~~~~~~~~~~~~~
* In Admin Panel add Database
    * Currently supported Databases: MYSQL, Postgres
* Add port, username and password
* Password is encrypyed in database
* Make sure account is readonly only (http://www.symantec.com/business/support/index?page=content&id=HOWTO30408)
* Tags affect the security and visibility of a query

Creating a Query
~~~~~~~~~~~~~~~~
* In Admin Panel add Query
* Provide descriptions in short and long description.  Short shows up on index page, long does not.
* Enter SQL as it is to run in the SQL area.  Formatting provided by Ace.JS
* Limits will be added automatically unless limits are detected.
* Choose database to run against.
* Set query replacement parameters.  These will search for strings in the Query and replace with parameters provided by user.  These will not be sanitized and present a possible injection source, which is why it is important to only use a readonly account.
* Pivot will turn a three column query of the form A / B / C and pivot A against B with values C.  Nulls will be filled with 0.
* If a query has a chart, the chart will be saved when it is saved and displayed as a thumbnail on the index page

Precedent Queries
~~~~~~~~~~~~~~~~~
* Queries can incldue precent queries.
* Those queries will run before the target query.
* Results are saved into a local database (currently named test/ to be named temp).  Temp can be accessed as its own database, and a query execution tree could join results from two queiries in temp.
* Precedents are executed in serial.
* Cycle detection is not performed.

Charting Options
~~~~~~~~~~~~~~~~
* Line, Bar, Column, scatter
* Stacked
* Log x/y axis.
* Highcharts handles the rest.
* Inject Highcharts JS (TODO improve UI) to allow arbitrary Highcharts extensibility

Viewing a Query
~~~~~~~~~~~~~~~
* Go to the index page and click through
* The URL will be persistant and can be sent via email
* Anyone with permission can view
* In the search box a particular row can be filtered for
* CSV can be saved from this view
* If the author has enabled parameterization, query parameters can be changed at the bottom of the query and rerun.
* Multiple Queries can be viewed at the same time by separating the ids with a comma.  All will have the same parameters given from the parameter set at the bottom

Setting up a Dashboard
~~~~~~~~~~~~~~~~~~~~~~
* A Dashboard is an ordered set of queries.
* Dashboards can be found from the homepage in the same way as queries.
* Dashboards wtih parameterization will be run with the same parameters if they are provided.

Setting up a Schedueled Emailed Report
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Dashboards only can be schedueled to run automatically and email results
* Email lists are set up for each report
* Emailed results will include default parameters

Groups and Permissions
~~~~~~~~~~~~~~~~~~~~~~
* Users can access data they have permission for.
* Tags are used not just to index queries, dashboards, and databases, but to give permission sets.
* Create a group with the same name as tag, to allow access to that query.
* A user will have access to the query iff:
    * They are a super user
    * The query and database are untagged
    * They are in a group that shares a name with the database or the query

CSV Upload
~~~~~~~~~~
* You can upload a csv to the scratch DB from the admin panel
* Header should be provided in the first row and formatting is auto-detected as best as possible.

Thanks
~~~~~~
* Django
* Jquery
* Jquery UI
* Django Taggit
* Django Favorits
* Django Encrpyed
* Highcharts
* PhantomJS
* Datatables JS
* ACE.js
* Django ACE
* Bootstrap
* Django Cron
