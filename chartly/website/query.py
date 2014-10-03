import models
import logging
import MySQLdb
import pandas as pd
import uuid
from django.conf import settings
import re

logger = logging.getLogger(__name__)
MAX_DEPTH_RECURSION = 10

class DataManager:
    def __init__(self, query_id = None, request = None, depth = 0):
        self.query_id = query_id
        self.query_text = None
        self.request = request
        self.depth = depth
        if depth > MAX_DEPTH_RECURSION:
            raise IOError("Recursion Limit Reached")
    def setQuery(self, query_text):
        self.query_text = query_text
        self.checkSafety()

    def setDB(self, db):
        self.db = models.Db.objects.filter(id = db)[0]

    def setPivot(self, pivot):
        self.pivot_data = pivot

    def prepareQuery(self):
        # Get Query From Database
        q = models.Query.objects.filter(id = self.query_id)[0]
        # Set up query and DB and pivot
        self.setQuery(q.query_text)
        self.setDB(q.database_id)
        self.setPivot(q.pivot_data)

        #logging.error('QUERY IS NOW BEFORE DEFUALTS: %s' % (self.query_text))
        self.defaultFind() 
        #logging.error('QUERY IS NOW AFTER DEFUALTS: %s' % (self.query_text))
        # Set default Values
        self.defaultSet()
        #logging.error('QUERY IS NOW AFTER UPDATES: %s' % (self.query_text))
        # Attach Limits
        if q.insert_limit == True:
            self.addLimits()
        # Run safety/sanity check for deletes/updates/...
        self.checkSafety()
        logging.info('QUERY IS NOW : %s' % (self.query_text))

    def runQuery(self):
        
        # Get DB creds
        if self.db.type  == 'MySQL':
            self.runMySQLQuery()
        elif self.db.type == 'Postgres':
            self.runPostgresQuery()
        elif self.db.type == 'Hive':
            self.runHiveQuery()
        if len(self.data) == 0:
            raise Exception("No Data Returned")
        #logger.warning("PIVOT STATE %s " % self.pivot_data)
        if self.pivot_data == True:
            self.pivot()
        self.pandasToArray()
        logging.warning("TO NUMERICALZE NOW")
        self.numericalizeData()

        return self.data_array
    def setPrecedents(self):
        # Will find precents for the particular query ID and run them, saving output
        # to the local DB
        QP = QueryPrecents.objects.filter(final_query_id = self.query_id)
        for i in QP: # TODO could be parralelized???
            DM = DataManager(QP.preding_query_id, request, self.depth + 1)
            DM.prepareQuery()
            DM.runQuery()
            DM.saveToSQLTable()

    def runMySQLQuery(self):
        #TODO optimize
        con = MySQLdb.connect(host = self.db.host, port = self.db.port, 
                user = self.db.username, passwd =self.db.password_encrpyed,
                db = self.db.db)
        data = pd.io.sql.read_sql(self.query_text,con)
        self.data = data
        self.data_pandas = data
        con.close()

    def runPostgresQuery(self):
        # TODO write this
        con = psycopg2.connect(host = self.db.host, port = self.db.port, 
                    username = self.db.username, password =self.db.password_encrpyed)
        data = pd.io.sql.read_sql(self.query_text,con)
        self.data = data
        con.close()

    def runHiveQuery(self):
        # TODO write this
        con = MySQLdb.connect(host = self.db.host, port = self.db.port, 
                    username = self.db.username, password =self.db.password_encrpyed)
        data = pd.io.sql.read_sql(self.query_text,con)
        self.data = data
        con.close()

    def checkSafety(self):
        # Check for dangerous database things
        stop_words = ['insert','delete','drop','truncate','alter','grant']
        for word in stop_words:
            #logger.error("WAHOO; %s \n %s" % (word, self.query_text))
            if re.match(self.query_text, word) != None:
                raise IllegalCondition
        # TODO check for major ass subselects, dumbass joins and other dumb-ass shit like that!

    def addLimits(self):
        # Adds limit 1000 to the end of the query
        # TODO check that limits are already not there
        if len(re.findall('limit(\s)*(\d)*(\s)*(;)(\s)*?$', self.query_text)) == 0:
            # check for semicolon
            if len(re.findall('[;](\s)*$', self.query_text)) == 0: # No Semicolon
                self.query_text += " limit 1000;"
            else: #semicolon
                self.query_text = re.sub('[;](\s)*$','', self.query_text) + 'limit 1000;'

    def pivot(self):
        # use pandas TODO to make the pivot
        #logging.warning(self.data)
        df2 = pd.pivot_table(self.data, values=self.data.columns[2],
                index = self.data.columns[0],
                columns = self.data.columns[1]).fillna(0)
        df2.reset_index(level=0, inplace=True)

        self.data = df2
        #logging.warning(self.data)
        
    def pandasToArray(self):
        """ Convert from panadas format to array of arrays
        """
        data_output = [self.data.columns]
        data_output += [[v for v in row[1]] for row in self.data.iterrows()]
        self.data_array = data_output

    def saveToSQLTable(self, table_name = None):
        if table_name is None:
            table_name = 'table_%s' % self.query_id
        db = settings.DATABASES['write_to']
        con = MySQLdb.connect(host = db['HOST'], port = db['PORT'], 
                    user = db['USER'], passwd = db['PASSWORD'], db = db['NAME'])
        #data_to_write = self.data_pandas
        #data_type = type(data_to_write)
        #
        self.data_pandas.to_sql(table_name, con, flavor='mysql', if_exists='replace')
        con.close() 

    def numericalizeData(self):
        # Checks for numbers encoded as strings due to bad database encoding
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
            self.replacement_dict[value_object.search_for] = {'data_type' : value_object.data_type,
                                                   'search_for' : value_object.search_for,
                                                   'replace_with' : self.request.GET.get(value_object.search_for, value_object.replace_with_cleaned())}
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
        #raise ValueError('go fuck yourself')