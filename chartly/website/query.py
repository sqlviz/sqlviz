import models
import logging
import MySQLdb
import pandas as pd
import uuid
from django.conf import settings
import re
import psycopg2
import sqlalchemy
from urllib import quote_plus as urlquote
import copy

logger = logging.getLogger(__name__)
MAX_DEPTH_RECURSION = 10

class DataManager:
    def __init__(self, query_id = None, request = None, depth = 0,
                pivot_data = None, cumulative = None):
        self.query_id = query_id
        self.query_text = None
        self.request = request
        self.depth = depth
        if depth > MAX_DEPTH_RECURSION:
            raise IOError("Recursion Limit Reached")
        self.pivot_data = pivot_data
        self.cumulative = cumulative
        if self.request is not None:
            self.user = self.request.user
        else:
            self.user = None
        self.query = None # TODO find a better way around this

    def logQueryUsage(self):
        """
        Saves query browsing for ACL purposes
        """
        if self.user is None or self.query is None:
            logging.info("Runnig query without a user or query")
        else:
            QV = models.QueryView(user = self.user,
                query = self.query)
            QV.save()

    def setQuery(self, query_text):
        """
        Takes a query_text and sets it to the self.query_text
        """
        self.query_text = query_text

    def setDB(self, db):
        """
        Takes a DB_id and sets it
        """
        self.db = models.Db.objects.filter(id = db)[0]

    def setPivot(self, pivot):
        """
        Set pivot state to True/False
        """
        self.pivot_data = pivot

    def setCumulative(self, cumulative):
        """
        Set cumulative state to True / False
        """
        self.cumulative = cumulative

    def prepareQuery(self):
        """
        Prepares self query, by pulling query from DB, 
        setting DB, Pivot and cumulative.
        Then sets defaults, limits, and checks safety
        """
        self.query = models.Query.objects.filter(id = self.query_id)[0]
        # Set up query and DB and pivot
        self.setQuery(self.query.query_text)
        self.setDB(self.query.database_id)
        self.setPivot(self.query.pivot_data)
        self.setCumulative(self.query.cumulative)
        self.defaultFind() 
        # Set default Values
        self.defaultSet()
        # Attach Limits
        if self.query.insert_limit == True:
            self.addLimits()
        #logging.info('QUERY IS NOW : %s' % (self.query_text))

    def addQueryComments(self):
        """
        Adds comments before query for the DBAs to blame
        """
        if self.db == 'MySQL':
            comment = "#"
        else:
            comment = "--"
        self.query_text = "%s Chartly Running Query Id: %s \n %s" % (comment, self.query_id, self.query_text)
    def runQuery(self):
        """
        Runs self's query against DB and then does post-processing
        like pivots, cumulative, etc
        """
        # Run safety/sanity check for deletes/updates/...
        PermissionToView(self.user, self.query).check_permission()

        self.checkSafety() # TODO this is run twice
        self.addQueryComments()
        self.logQueryUsage()
        

        # Get DB creds
        if self.db.type in ['MySQL','Postgres']:
            self.runSQLQuery()
        elif self.db.type == 'Hive':
            self.runHiveQuery()
        else:
            raise ValueError('DB Type not in MySQL, Postgres, Hive')

        if len(self.data) == 0:
            raise Exception("No Data Returned")
        #logger.warning("PIVOT STATE %s " % self.pivot_data)
        if self.pivot_data == True:
            self.pivot()
        if self.cumulative == True:
            self.data = self.data.cumsum()
        self.pandasToArray()
        #logging.warning("TO NUMERICALZE NOW")
        self.numericalizeData()

        return self.data_array

    def setPrecedents(self):
        """
        Will find precents for the particular query ID and run them, saving
        output to the local DB
        """
        QP = QueryPrecents.objects.filter(final_query_id = self.query_id)
        for i in QP: # TODO could be parralelized???
            DM = DataManager(QP.preding_query_id, request, self.depth + 1)
            DM.prepareQuery()
            DM.runQuery()
            DM.saveToSQLTable() # TODO run this after pivot?

    def runSQLQuery(self):
        #TODO optimize
        engine_string = '%s://%s:%s@%s:%s/%s' % (
                self.db.type.lower(), 
                self.db.username,
                urlquote(self.db.password_encrypted),
                self.db.host, 
                self.db.port, 
                self.db.db)
        engine = sqlalchemy.create_engine(engine_string,)
        c = engine.connect()
        query_text = self.query_text.replace('%','%%') # SQLAlchemy Escaping
        result = c.execute(query_text)
        df = pd.DataFrame(result.fetchall())

        if df.shape == (0,0):
            raise Exception("No Data Returned by Query!")
        df.columns = result.keys()
        c.close()

        self.data = df
        self.data_pandas = copy.deepcopy(df)

    def runHiveQuery(self):
        # TODO write this
        con = MySQLdb.connect(host = self.db.host, port = self.db.port, 
                    username = self.db.username,
                    password = self.db.password_encrpyed)
        data = pd.io.sql.read_sql(self.query_text,con)
        self.data = data
        con.close()

    def checkSafety(self):
        # Check for dangerous database things
        stop_words = ['insert','delete','drop','truncate','alter','grant']
        for word in stop_words:
            #logger.error("WAHOO; %s \n %s" % (word, self.query_text))
            if word in self.query_text.lower():
                raise IllegalCondition
        # TODO check for major ass subselects, dumbass joins and other dumb-ass
        # shit like that!

    def addLimits(self):
        # Adds limit 1000 to the end of the query
        # TODO check that limits are already not there
        if len(re.findall('limit(\s)*(\d)*(\s)*(;)(\s)*?$', self.query_text)) == 0:
            # check for semicolon
            if len(re.findall('[;](\s)*$', self.query_text)) == 0: # No Semicolon
                self.query_text += " limit 1000;"
            else: #semicolon
                self.query_text = re.sub('[;](\s)*$','', self.query_text) + \
                        ' limit 1000;'

    def pivot(self, null_fill = None):
        """
        Pivots data along first and second columns
        Fills nulls as null_fill (defaults to 0)
        resets self.data with pivoted data
        """
        # use pandas TODO to make the pivot
        #logging.warning(self.data)
        if len(set(self.data.columns)) != len(self.data.columns):
            raise ValueError("Two or more columns have the same name")
        df2 = pd.pivot_table(self.data, values=self.data.columns[2],
                index = self.data.columns[0],
                columns = self.data.columns[1]).fillna(null_fill)
        df2.reset_index(level=0, inplace=True)

        self.data = df2
        
    def pandasToArray(self):
        """
        Convert from panadas format to array of arrays
        """
        data_output = [self.data.columns]
        data_output += [[v for v in row[1]] for row in self.data.iterrows()]
        self.data_array = data_output

    def returnHTMLTable(self):
        """
        Returns a Pandas HTML Array from the data DataFrame
        """
        return(self.data.to_html(index= False))

    def saveToSQLTable(self, table_name = None):
        """
        Writes output to SQL table
        Is not highly-stable due
        """
        if table_name is None:
            table_name = 'table_%s' % self.query_id
        db = settings.DATABASES['write_to']
        con = MySQLdb.connect(host = db['HOST'], port = db['PORT'], 
                    user = db['USER'], passwd = db['PASSWORD'], db = db['NAME'])
        #data_to_write = self.data_pandas
        #data_type = type(data_to_write)
        
        self.data_pandas.to_sql(table_name, con, flavor='mysql',
                    if_exists='replace')
        con.close() 

    def numericalizeData(self):
        """
        Checks for numbers encoded as strings due to bad database encoding
        """
        def num(foo):
            #try:
            #    return float(foo)
            #except (ValueError, TypeError) as e:
            try:
                return float(foo)
            except (ValueError, TypeError) as e:
                return foo
        new_data = [[num(foo) for foo in row] for row in self.data_array]                
        self.data_array = new_data

    def defaultFind(self):
        # Find default values, compare with those in request, and update those defaults
        # that are over-riden by client values
        # Get values from DB
        value_objects = models.QueryDefault.objects.filter(query_id = self.query_id)
        self.replacement_dict = {}
        for value_object in value_objects:
            # Compare with those from client request
            self.replacement_dict[value_object.search_for] = {
                    'data_type' : value_object.data_type,
                    'search_for' : value_object.search_for,
                    'replace_with' : 
                            self.request.GET.get(value_object.search_for,
                                    value_object.replace_with_cleaned())
            }
        return self.replacement_dict
        """# Ensure Data Types are appropriate ?
        if value_objects[key].type == "Numeric":
            target_value = float(target_value)
        elif value_objects[key].type == "String":
            target_value = str(target_value) #TODO check that there are no SQL injections here!
        elif value_objects[key].type == "Date":
            target_value = target_value # Regexes to YYYY-MM-DD"""

    def defaultSet(self):
        # For values in the replacement dict, update the self.query_text
        # Replace key with target_value
        for key, replacement_dict in self.replacement_dict.iteritems():
            self.query_text = self.query_text.replace(replacement_dict['search_for'], str(replacement_dict['replace_with']))

class PermissionToView():
    def __init__(self, user = None, query = None):
        self.user = user
        self.query = query

    def check_permission(self):
        """
        return true is user has permission on query, false otherwise
        """
        if self.user is None:
            return True # TODO THIS BYPASSES UNAUTHENTICATED USERS AND MAY BE BAD?
        if self.user.is_active == False:
            logging.warning("NOT ACTIVE")
            raise Exception("User is not Active!")
            return False
        if self.user.is_superuser == True:
            logging.warning("SUPER USER")
            return True
        user_groups = self.user.groups.values_list('name',flat=True)
        db_tags = [str(i) for i in self.query.database.tags.all()]
        query_tags = [str(i) for i in self.query.tags.all()]
        logging.warning("USER %s DB %s Query %s Required %s" % 
            (
                user_groups, db_tags, query_tags,
                list(set(db_tags) | set(user_groups))
            ))
        if len(list(set(db_tags) & set(user_groups))) > 0 \
                or len(list(set(query_tags) & set(user_groups))) > 0:
            return True
        elif len(db_tags) == 0 or len(query_tags) == 0: # No Permissions set
            return True
        else:
            raise Exception("User does not have permission to view.  Requires membership in at least one of these groups:  %s " %  list(set(db_tags) | set(query_tags)))
            return False


class MySQLManager:
    def __init__(self, db):
        self.DM = DataManager()
        self.DM.db = db # TODO make this use setDb

    def runQuery(self):
        return self.DM.runQuery()

    def findDatabase(self):
        self.DM.query_text = "show databases"

    def showTables(self, db):
        self.DM.query_text = "show tables in %s" % (db)

    def describeTable(self, db, table):
        self.DM.query_text = "describe %s.%s" % (db, table)

    def describeIndexTable(self, db, table):
        self.DM.query_text =  "show index from %s in %s" % (table, db)

class PSQLManager:
    def __init__(self, db):
        self.DM = DataManager()
        self.DM.db = db # TODO make this use setDb

    def runQuery(self):
        return self.DM.runQuery()

    def findDatabase(self):
        self.DM.query_text = """SELECT datname FROM pg_database
            WHERE datistemplate = false;"""

    def showTables(self, db):
        self.DM.query_text = """SELECT table_name
            FROM information_schema.tables
            where table_catalog = '%s' and table_schema = 'public'
            ORDER BY table_schema,table_name;""" % (db)

    def describeTable(self, db, table):
        self.DM.query_text = """SELECT
                column_name, data_type, character_maximum_length
            FROM
                INFORMATION_SCHEMA.COLUMNS
            where
                table_catalog = '%s' and table_name = '%s'""" % (db, table)

    def describeIndexTable(self, db, table):
        self.DM.query_text =  "show index from %s in %s" % (table, db)        