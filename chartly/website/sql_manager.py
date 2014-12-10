import query
class Manager:
    def __init__(self, db, request):
        self.RQ = query.Manipulate_Data(query_text = '',
                db = db,
                user = request.user)

    def run_query(self):
        self.RQ.run_query()
        return self.RQ.pandas_to_array()

class MySQLManager(Manager):
    def findDatabase(self):
        self.RQ.query_text = "show databases"

    def showTables(self, db):
        self.RQ.query_text = "show tables in %s" % (db)

    def describeTable(self, db, table):
        self.RQ.query_text = "describe %s.%s" % (db, table)

    def describeIndexTable(self, db, table):
        self.RQ.query_text =  "show index from %s in %s" % (table, db)

class PSQLManager(Manager):
    def findDatabase(self):
        self.RQ.query_text = """SELECT datname FROM pg_database
            WHERE datistemplate = false;"""

    def showTables(self, db):
        self.RQ.query_text = """SELECT table_name
            FROM information_schema.tables
            where table_catalog = '%s' and table_schema = 'public'
            ORDER BY table_schema,table_name;""" % (db)

    def describeTable(self, db, table):
        self.RQ.query_text = """SELECT
                column_name, data_type, character_maximum_length
            FROM
                INFORMATION_SCHEMA.COLUMNS
            where
                table_catalog = '%s' and table_name = '%s'""" % (db, table)

    def describeIndexTable(self, db, table):
        self.RQ.query_text =  "show index from %s in %s" % (table, db)        