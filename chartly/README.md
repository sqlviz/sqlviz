# Chartly

## Introduction

Chartly is a data visualization platform built on Django

## Deploy

```
Pip install requirements.txt -r
```
Create a MySQL Database with access locally. 

### MySQL 
TODO add this to deploy.sh
```
CREATE DATABASE IF NOT EXISTS DJANGO;
CREATE USER DJANGO IDENTIFIED BY DJANGO;
GRANT ALL ON DJANGO.* TO DJANGO;
```

### Create Django Encryped Keys

```
mkdir fieldkeys
keyczart create --location=fieldkeys --purpose=crypt
keyczart addkey --location=fieldkeys --status=primary --size=256
```

### Setting Up

Follow these steps in the chartly folder to set up django and run the test server
```
cd chartly
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
````

### Using Chartly

#### Setting up a database
* In Admin Panel add Database
  * Currently supported Databases: MYSQL, Postgres
* TODO: Oracle, MSSQL, Hive 2, GBQ
* Add port, username and password
* Password is encrypyed in database
* Make sure account is readonly only (http://www.symantec.com/business/support/index?page=content&id=HOWTO30408)

#### Creating a Query
* In Admin Panel add Query
* Provide descriptions in short and long description.  Short shows up on index page, long does not.
* Enter SQL as it is to run in the SQL area.  Formatting provided by Ace.JS
* Limits will be added automatically unless limits are detected.
* Choose database to run against.
* Set query replacement parameters.  These will search for strings in the Query and replace with parameters provided by user.  These will not be sanitized and present a possible injection source, which is why it is important to only use a readonly account.
* Pivot will turn a three column query of the form A / B / C and pivot A against B with values C.  Nulls will be filled with 0.

#### Precedent Queries
* Queries can incldue precent queries.
* Those queries will run before the target query.
* Results are saved into a local database (currently named test/ to be named temp).  Temp can be accessed as its own database, and a query execution tree could join results from two queiries in temp. 
* Precedents are executed in serial.
* Cycle detection is not performed.

#### Charting Options
* Line, Bar, Column, scatter
* Stacked
* Log x/y axis.
* Highcharts handles the rest.
* Inject Highcharts JS (TODO improve UI) to allow arbitrary Highcharts extensibility

#### Viewing a Query
* Go to the index page and click through
* The URL will be persistant and can be sent via email
* Anyone with permission can view
* In the search box a particular row can be filtered for
* CSV can be saved from this view
* If the author has enabled parameterization, query parameters can be changed at the bottom of the query and rerun.
* Multiple Queries can be viewed at the same time by separating the ids with a comma.  All will have the same parameters given from the parameter set at the bottom

#### Setting up a Dashboard
* A Dashboard is an ordered set of queries.
* Dashboards can be found from the homepage in the same way as queries.
* Dashboards wtih parameterization will be run with the same parameters if they are provided.

#### Setting up a Schedueled Emailed Report
* Dashboards only can be schedueled to run automatically and email results
* Email lists are set up for each report
* Emailed results will include default parameters

#### Groups and Permissions
* Users can access data they have permission for.  
* Tags are used not just to index queries, dashboards, and databases, but to give permission sets.
* Create a group with the same name as tag, to allow access to that query.
* A user will have access to the query iff:
  * They are a super user
  * The query and database are untagged
  * They are in a group that shares a name with the database or the query


#### Licensing
* Highcharts licensing is required.
  * http://shop.highsoft.com/highcharts.html

#### Thanks
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