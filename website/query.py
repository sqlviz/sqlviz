from django.conf import settings
from django.conf import settings

from urllib import quote_plus as urlquote
import logging
import MySQLdb
import pandas as pd
import uuid
import re
import psycopg2
import sqlalchemy
import os
import json
import subprocess
import sys
import copy

import models
from date_time_encoder import *

logger = logging.getLogger(__name__)
MAX_DEPTH_RECURSION = 10

class Query:
    def __init__(self, query_text, db, depth = 0, user = None,
                query_id = None, query_model = None, parameters = None):
        self.query_text = query_text
        self.db = db
        self.query_id = query_id
        self.user = user
        self.depth = depth
        self.query_model = query_model
        self.parameters = parameters
        if depth > MAX_DEPTH_RECURSION:
            raise IOError("Recursion Limit Reached")

    def set_query_text(self, query_text):
        self.query_text = query_text

    def check_safety(self):
        """
        Check for dangerous database things
        """
        stop_words = ['insert','delete','drop','truncate','alter','grant']
        for word in stop_words:
            if word in self.query_text.lower():
                raise IllegalCondition("Query contained %s -- Can not be run" % word)
        # TODO check for other questionable queries

    def add_limit(self):
        """
        Adds limit 1000 to the end of the query
        """
        if len(re.findall('limit(\s)*(\d)*(\s)*(;)(\s)*?$',
                self.query_text)) == 0:
            # check for semicolon
            if len(re.findall('[;](\s)*$', self.query_text)) == 0:
                # No Semicolon
                self.query_text += " limit 1000;"
            else:
                # Semicolon exists
                self.query_text = re.sub('[;](\s)*$','',
                        self.query_text) + ' limit 1000;'

    def add_comment(self):
        """
        Adds comments before query for the DBAs to blame
        """
        comment_char = {'MySQL' : '#','Postgres':'--','Hive' : '--'}
        self.query_text = "%s Chartly Running Query Id: %s \n %s" % (
                comment_char[self.db.type], self.query_id,
                self.query_text)

    def prepare_safety(self):
        """
        Runs safety check and adds limit if it is in the model
        """
        self.check_safety()
        if self.query_model is not None:
            if self.query_model.insert_limit == True:
                self.add_limit()
        self.add_comment()


class Load_Query:
    def __init__(self, query_id, user,parameters = {},
                ):
        self.query_id = query_id
        self.user = user
        self.parameters = parameters

    def load_query(self):
        """
        Load from model
        Set parameters
        create Query Object
        """
        query = models.Query.objects.filter(id = self.query_id)[0]
        # Manipulate is the final form of Query
        self.query = Manipulate_Data(query_text = query.query_text,
                    db = query.db, user = self.user,
                    query_id = self.query_id, query_model = query,
                    parameters = self.parameters)
        
    def parameters_find(self):
        """
        Find default values, compare with those in request, and update
        those defaults that are over-riden by client values Get values
        from DB
        """
        preset_parameters = models.QueryDefault.objects.filter(query_id = 
                self.query_id)
        target_parameters = {}
        if self.parameters is not None:
            for parameter in self.parameters:
                # Compare with those from client request
                if parameter.search_for in parameters:
                    replace_with = parameters[parameter.search_for]
                else:
                    replace_with = parameter.replace_with_cleaned()
                target_parameters[parameter.search_for] = {
                        'data_type' : parameter.data_type,
                        'search_for' : parameter.search_for,
                        'replace_with' : replace_with
                }
        self.target_parameters = target_parameters

    def parameters_replace(self):
        """
        For values in the target_parameters dict, update the query_text
        Replace key with target_value
        """
        for key, replacement_dict in  self.target_parameters.iteritems():
            self.query.query_text = self.query.query_text(
                    replacement_dict['search_for'],
                    str(replacement_dict['replace_with']))

    def get_parameters(self):
        return self.target_parameters

    def prepare_query(self):
        self.load_query()
        self.parameters_find()
        self.parameters_replace()
        #self.parameters_replace()
        return self.query

class Run_Query(Query):
    def check_permission(self):
        """
        return true is user has permission on query, false otherwise
        """
        user = self.user
        if self.user is None:
            # TODO THIS BYPASSES UNAUTHENTICATED USERS AND MAY BE BAD?
            return True 
        if self.user.is_active == False:
            #logging.warning("NOT ACTIVE")
            raise Exception("User is not Active!")
            return False
        if self.user.is_superuser == True:
            #logging.warning("SUPER USER")
            return True
        user_groups = set(self.user.groups.values_list('name',flat=True))
        db_tags = set([str(i) for i in self.db.tags.all()])
        if self.query_model is None: # Interactive Modes
            query_tags = set() # Give empty set
        else:
            query_tags = set([str(i) for i in self.query_model.tags.all()])
        union_set = db_tags | query_tags
        if len(union_set & user_group)  > 0:
            # User tag is in either query or DB set
            return True
        elif len(db_tags) == 0:
            # No Permissions set at either user or DB level
            return True
        else:
            raise Exception("""User does not have permission to view. 
                Requires membership in at least one of these groups:  %s
                """ %  (union_set))
            return False

    def record_query_execution(self):
        """
        Saves query browsing for ACL purposes
        """
        if self.user is None or self.query_id is None:
            logging.info("Runnig query without a user or query")
        else:
            QV = models.QueryView(user = self.user,
                query = self.query_model)
            QV.save()

    def return_data_array(self):
        return self.data

    def save_to_mysql(self, table_name = None):
        """
        Writes output to MySQL table
        Pandas is depricating this function.  TODO rewrite
        """
        if table_name is None:
            table_name = 'table_%s' % self.query_id
        db = settings.DATABASES['write_to']
        con = MySQLdb.connect(host = db['HOST'], port = db['PORT'], 
                    user = db['USER'], passwd = db['PASSWORD'], db = db['NAME'])
        
        self.data.to_sql(table_name, con, flavor='mysql',
                    if_exists='replace')
        con.close()
        QC = models.QueryCache.objects.filter(query = self.query_model).filter(table_name = table_name).first()
        
        if QC is None:
            models.QueryCache.objects.create(query = self.query_model,
                    table_name = table_name)
        else:
            QC.save()

        return table_name

    def run_precedents(self):
        QP = models.QueryPrecedent.objects.filter(final_query_id = self.query_id)
        run_guid = uuid.uuid1()

        for i in QP: # TODO could be parralelized???
            # TODO 
            LQ = Load_Query(query_id = QP.preceding_query_id,
                        user = self.user,
                        parameters = self.parameters)
            Q = LQ.run()
            Q.run_query()
            table_name = '%s_%s' % (run_guid, LQ.query_id)
            Q.save_to_mysql(table_name) # TODO run this after pivot?        

    def run_query(self):
        """
        Wrapper for Run Query
        """
        self.prepare_safety()
        self.check_permission()
        self.record_query_execution()
        
        # Run Precedents
        self.run_precedents()
        # Get DB creds
        if self.db.type in ['MySQL','Postgres']:
            data = self.run_SQL_query()
        elif self.db.type == 'Hive':
            raise ValueError("HIVE NOT YET IMPLMENTED TODO")
        else:
            raise ValueError('DB Type not in MySQL, Postgres, Hive')

        if len(data) == 0:
            raise Exception("No Data Returned")
        self.data = data
        return data

    def run_SQL_query(self):
        """
        Runs SQL query in DB
        """
        engine_string = '%s://%s:%s@%s:%s/%s' % (
                self.db.type.lower(), 
                self.db.username,
                urlquote(self.db.password_encrypted),
                self.db.host, 
                self.db.port, 
                self.db.db)
        engine = sqlalchemy.create_engine(engine_string,)
        c = engine.connect()
        query_text = self.query_text.replace('%','%%') # SQLAlchemy Esc
        result = c.execute(query_text)
        df = pd.DataFrame(result.fetchall())

        if df.shape == (0,0):
            raise Exception("No Data Returned by Query!")
        df.columns = result.keys()
        c.close()

        return df

class Manipulate_Data(Run_Query):

    def numericalize_data_array(self):
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
        return self.data_array

    def pivot(self, null_fill = 0):
        # use pandas TODO to make the pivot
        #logging.warning(self.data)
        if len(set(self.data.columns)) != len(self.data.columns):
            raise ValueError("Two or more columns have the same name")
        df2 = pd.pivot_table(self.data, values=self.data.columns[2],
                index = self.data.columns[0],
                columns = self.data.columns[1]).fillna(null_fill)
        df2.reset_index(level=0, inplace=True)
        self.data = df2
        return self.data

    def cumulative(self, axis = None, percent = None, relative_to = None):
        """
        TODO Make this actually do cumulative statistics
        """
        self.data = self.data.cumsum()

    def rotate(self):
        """
        transpose data
        """
        self.data = self.data.transpose()

    def pandas_to_array(self):
        #logging.warning(self.data)
        self.data_array = [self.data.columns]
        self.data_array += [[v for v in row[1]] for row in self.data.iterrows()]
        #logging.warning(self.data_array)
        return self.data_array

    def html_table(self):
        """
        Returns a Pandas HTML Array from the data DataFrame
        """
        return(self.data.to_html(index= False))
    def generate_image(self, file_output = None, width = 400, height = 300):
        """
        create a picture!
        """
        data = copy.deepcopy(self.data_array)
        columns = data.pop(0)
        graph_data= { 
                'columns' : columns,
                'data' : data,
                'chart_type':self.query_model.chart_type,
                'graph_extra': self.query_model.graph_extra,
                'yAxis_log' : self.query_model.log_scale_y,
                'stacked' : self.query_model.stacked,
                'xAxis' : '', 'yAxis' : '',
                'graph_extra' : self.query_model.graph_extra,
                'title' : self.query_model.title
            }
        static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'website/static'))
        #logging.warning(static_path)
        guid = str(uuid.uuid1())
        json_data_file = '//tmp/%s.json' % (guid)
        cli = """phantomjs %s/js/phantom_make_chart.js '%s' %s""" % (
                static_path, json.dumps(graph_data, cls = DateTimeEncoder), json_data_file)
        #print cli
        #logging.warning(cli)
        subprocess.call([cli], shell = True)
        # Transform JSON file into image using CLI and Phantom JS
        if file_output == None:
            output_image = '%sthumbnails/%s.png' % (settings.MEDIA_ROOT, self.query_id)
        else:
            output_image = file_output
        cli = """phantomjs %s/Highcharts-4.0.3/exporting-server/phantomjs/highcharts-convert.js -infile %s -outfile %s -scale 2.5 -width %s - height %s""" % (static_path, json_data_file, output_image, width, height)
        #print cli
        subprocess.call([cli], shell = True)
        return output_image

    def run_manipulations(self):
        """
        Gets Processing steps from DB and executes them in order
        """
        def exists_and_equals(dictionary, key, value):
            if key in dictionary:
                if dictionary[key] == value:
                    return True
            return False

        d = {}
        QP = models.QueryProcessing.objects.filter(query = self.query_id)
        for i in QP:
            d[i.attribute] = i.value

        if exists_and_equals(d, 'pivot','True'):
            self.pivot()
        if exists_and_equals(d,'rotate','True'):
            self.rotate()
        if exists_and_equals(d,'cumulative','True'):
            self.cumulative()
        self.pandas_to_array()
        self.numericalize_data_array()

        """if self.query_model.chart_type != 'None':
            # Run the graph in phantom JS
            self.generate_image(fileout)
            self.query_model.image = fileout
            self.query_model.save()
        """