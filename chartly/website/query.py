from models import *
import logging
import MySQLdb
import pandas
logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, query_id = None):
        self.query_id = query_id
        self.query_text = None
    def setQuery(self, query_text):
        self.query_text = query_text

    def prepareQuery(self):
        # Get Query From Database
        q = Query.objects.filter(id = self.query_id)[0]
        # SEt up query and DB
        self.query_text = q.query_text
        self.db = Db.objects.filter(id = q.database_id)[0]
        self.pivot_data = q.pivot_data
        # Replace with defaults
        #self.defaultUpdate() TODO make this work
        # Attach Limits
        if q.insert_limit == True:
            self.addLimits()
        # Run safety/sanity check
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
        logger.warning("PIVOT STATE %s " % self.pivot_data)
        if self.pivot_data == True:
            self.pivot()
        self.pandasToArray()
        self.numericalizeData()

        return self.data

    def runMySQLQuery(self):
        #TODO optimize
        con = MySQLdb.connect(host = self.db.host, port = self.db.port, 
                user = self.db.username, passwd =self.db.password_encrpyed,
                db = self.db.db)
        data = pandas.io.sql.read_sql(self.query_text,con)
        self.data = data

    def runPostgresQuery(self):
        # TODO write this
        con = MySQLdb.connect(host = self.db.host, port = self.db.port, 
                    username = self.db.username, password =self.db.password_encrpyed)
        data = pandas.io.sql.read_sql(self.query_text,con)
        self.data = data
    def runHiveQuery(self):
        # TODO write this
        con = MySQLdb.connect(host = self.db.host, port = self.db.port, 
                    username = self.db.username, password =self.db.password_encrpyed)
        data = pandas.io.sql.read_sql(self.query_text,con)
        self.data = data
    
    def checkSafety(self):
        # Check for dangerous database things
        stop_words = ['insert','delete','drop','truncate','alter','grant']
        for word in stop_words:
            logger.error("WAHOO; %s \n %s" % (word, self.query_text))
            if re.match(self.query_text, word) != None:
                raise IllegalCondition

    def addLimits(self):
        # TODO check that limits are already not there
        self.query_text += " limit 1000"

    def pivot(self):
        # use pandas TODO to make the pivot
        logging.warning(self.data)
        df2 = pandas.pivot_table(self.data, values=self.data.columns[2],
                index = self.data.columns[0],
                columns = self.data.columns[1]).fillna(0)
        df2.reset_index(level=0, inplace=True)

        self.data = df2
        logging.warning(self.data)
        
    def pandasToArray(self):
        # Convert from panadas format to array of arrays
        #data_dict = self.data.to_dict(outtype='records')
        #logging.warning(data_dict[0])
        data_output = []
        temp_row = []
        for k in self.data.columns:
            temp_row.append(k)
        data_output.append(temp_row)            
        for row in self.data.iterrows():
            temp_row = []
            for v in row[1]:
                temp_row.append(v)
            data_output.append(temp_row)
        self.data = data_output

    def numericalizeData(self):
        # Checks for numbers encoded as strings due to bad database encoding
        new_data = []
        for row in self.data:
            temp_row = []
            for value in row:
                try:
                    value = int(value)
                except:
                    try:
                        value = float(value)
                    except:
                        pass
                temp_row.append(value)
            new_data.append(temp_row)
        self.data = new_data

    def defaultUpdate(self):
        #TODO MAKE THIS WORK
        # Get values from DB
        value_objects = QueryDefault.objects.filter(query_id = self.query_id)
        for key in value_objects:
            target_value = self.request.get(i.search_for, i.replace_with)
            if value_objects[key].type=="Numeric":
                target_value = float(target_value)
            elif value_objects[key].type == "String":
                target_value = str(target_value) #Perhaps check for no SQL injections
            elif value_objects[key].type == "Date":
                # Regexes to YYYY-MM-DD
                pass

            # Replace key with target_value
            self.query_text.replace(key, target_value)