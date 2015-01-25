from django.conf import settings
from django.shortcuts import get_object_or_404

import logging
import pandas as pd
import uuid
import re

import sqlalchemy
import os
import json
import subprocess
import copy
import hashlib
import models
import get_db_engine
from urllib import quote_plus as urlquote

from date_time_encoder import DateTimeEncoder
logger = logging.getLogger(__name__)
MAX_DEPTH_RECURSION = 10


class Query:
    def __init__(self, query_text, db, depth=0, user=None,
                 query_id=None, query_model=None, parameters=None,
                 cacheable=True):
        self.query_text = query_text
        self.db = db
        self.query_id = query_id
        self.user = user
        self.depth = depth
        self.query_model = query_model
        self.parameters = parameters
        self.cacheable = cacheable
        if depth > MAX_DEPTH_RECURSION:
            raise IOError("Recursion Limit Reached")

    def check_safety(self):
        """
        Check for dangerous database things
        """
        stop_words = ['insert', 'delete', 'drop', 'truncate', 'alter', 'grant']
        for word in stop_words:
            if word in self.query_text.lower():
                raise RuntimeError(
                    "Query contained %s -- Can not be run" % word)
        # TODO check for other questionable queries

    def add_limit(self):
        """
        Adds limit 1000 to the end of the query if query does not
        currently have a limit set
        """
        if len(re.findall('limit(\s)*(\d)*(\s)*(;)?(\s)*?$',
                          self.query_text)) == 0:
            # check for semicolon
            if len(re.findall('[;](\s)*$', self.query_text)) == 0:
                # No Semicolon
                self.query_text += " limit 1000;"
            else:
                # Semicolon exists
                self.query_text = re.sub('[;](\s)*$', '',
                                         self.query_text) + ' limit 1000;'

    def add_comment(self):
        """
        Adds comments before query for the DBAs to blame
        """
        comment_char = {'MySQL': '#', 'Postgres': '--', 'Hive': '--'}
        self.query_text = "%s Chartly Running Query Id: %s \n %s" % (
            comment_char[self.db.type],
            self.query_id,
            self.query_text)

    def prepare_safety(self):
        """
        Runs safety check and adds limit if it is in the model
        Also saves hash before mutating query
        """
        self.check_safety()
        self.run_query_hash()
        if self.query_model is not None:
            if self.query_model.insert_limit is True:
                self.add_limit()
        self.add_comment()


class Load_Query:
    def __init__(self, query_id, user, cacheable=None,
                 parameters={}):
        self.query_id = query_id
        self.user = user
        self.cacheable = cacheable
        self.parameters = parameters

    def load_query(self):
        """
        Load from model
        Set parameters
        create Query Object
        """
        query = get_object_or_404(models.Query, pk=self.query_id)
        # Manipulate is the final form of Query
        if self.cacheable is None:  # User has not set
            self.cacheable = query.cacheable
        else:  # Convert to boolean
            self.cacheable = string_to_boolean(self.cacheable)
        self.query = Manipulate_Data(
            query_text=query.query_text, db=query.db, user=self.user,
            query_id=self.query_id, query_model=query,
            parameters=self.parameters, cacheable=self.cacheable)

    def parameters_find(self):
        """
        Find default values, compare with those in request, and update
        those defaults that are over-riden by client values Get values
        from DB
        """
        preset_parameters = models.QueryDefault.objects.filter(
            query_id=self.query_id)
        target_parameters = {}
        # if self.parameters is not None:
        for parameter in preset_parameters:  # self.parameters:
            # Compare with those from client request
            if parameter.search_for in self.parameters:
                replace_with = self.parameters[parameter.search_for]
                # TODO add data type check here
                # data_type = parameters.data_type
                # assert isinstance(replace_with, data_type)
            else:
                replace_with = parameter.replace_with_cleaned()

            target_parameters[parameter.search_for] = {
                'data_type': parameter.data_type,
                'search_for': parameter.search_for,
                'replace_with': replace_with}
        self.target_parameters = target_parameters

    def parameters_replace(self):
        """
        For values in the target_parameters dict, update the query_text
        Replace key with target_value
        """
        for key, replacement_dict in self.target_parameters.iteritems():
            self.query.query_text = self.query.query_text.replace(
                replacement_dict['search_for'],
                str(replacement_dict['replace_with']))

    def get_parameters(self):
        return self.target_parameters

    def prepare_query(self):
        self.load_query()
        self.parameters_find()
        self.parameters_replace()
        return self.query


class Run_Query(Query):
    def run_query_hash(self):
        m = hashlib.md5()
        m.update(self.query_text)
        self.query_hash = m.hexdigest()
        # logging.warning(self.query_hash)
        return self.query_hash

    def check_permission(self):
        """
        return true is user has permission on query, false otherwise
        """
        if self.user is None:
            # TODO THIS BYPASSES UNAUTHENTICATED USERS AND MAY BE BAD?
            return True
        if self.user.is_active is False:
            # logging.warning("NOT ACTIVE")
            raise Exception("User is not Active!")
            return False
        if self.user.is_superuser is True:
            # logging.warning("SUPER USER")
            return True
        user_groups = set(self.user.groups.values_list('name', flat=True))
        db_tags = set([str(i) for i in self.db.tags.all()])
        if self.query_model is None:  # Interactive Modes
            query_tags = set()  # Give empty set
        else:
            query_tags = set([str(i) for i in self.query_model.tags.all()])
        union_set = db_tags | query_tags
        if len(union_set & user_groups) > 0:
            # User tag is in either query or DB set
            return True
        elif len(db_tags) == 0:
            # No Permissions set at either user or DB level
            return True
        else:
            raise Exception("""User does not have permission to view.
                Requires membership in at least one of these groups:  %s
                """ % (union_set))
            return False

    def record_query_execution(self):
        """
        Saves query browsing for ACL purposes
        """
        if self.user is None or self.query_id is None:
            logging.error("Running query without a user or query")
        else:
            QV = models.QueryView(user=self.user, query=self.query_model)
            QV.save()

    def return_data_array(self):
        return self.data

    def save_to_mysql(self, table_name=None, batch_size=1000):
        """
        Writes output to MySQL table
        Pandas is depricating this function.  TODO rewrite
        """
        if table_name is None:
            table_name = 'table_%s' % self.query_id
        engine = get_db_engine.get_db_engine()
        # TODO put in limits for data size (cols x rows to insert data)
        self.data.to_sql(table_name, con=engine, if_exists='replace',
                         index=False, chunksize=batch_size)
        # logging.warning('Save to MySQL')
        QC = models.QueryCache.objects.filter(query=self.query_model).filter(table_name=table_name).first()
        # logging.warning(QC)
        if QC is None:
            # logging.warning('CREATE SOMETHING')
            models.QueryCache.objects.create(query=self.query_model,
                                             table_name=table_name,
                                             hash=self.query_hash)
        else:
            # logging.warning('modify something')
            QC.hash = self.query_hash
            QC.save()
        return table_name

    def run_precedents(self):
        QP = models.QueryPrecedent.objects.filter(final_query_id=self.query_id)
        run_guid = uuid.uuid1()

        for i in QP:  # TODO could be parralelized???
            LQ = Load_Query(
                query_id=QP.preceding_query_id,
                user=self.user,
                parameters=self.parameters,
                cacheable=True)
            Q = LQ.run()
            Q.run_query()
            table_name = '%s_%s' % (run_guid, LQ.query_id)
            Q.save_to_mysql(table_name)  # TODO run this after pivot?

    def run_query(self):
        """
        Wrapper for Run Query
        """
        self.prepare_safety()
        self.check_permission()
        self.record_query_execution()

        # Run Precedents
        self.run_precedents()
        # Attempt to use Cache
        table_cache = self.check_cache()
        # logging.warning('Cache Tables %s %s' % (table_cache, self.cacheable))
        if table_cache and self.cacheable:
            try:
                self.retrieve_cache(table_cache)
                self.cached = True
                return self.data
            except Exception, e:
                logging.error("""CACHE IS MISSING FOR TABLE
                        %s -- %s""" % (table_cache, str(e)))
        # Get DB Type
        if self.db.type in ['MySQL', 'Postgres']:
            self.cached = False
            self.data = self.run_SQL_query()
        elif self.db.type == 'Hive':
            raise ValueError("HIVE NOT YET IMPLMENTED TODO")
        else:
            raise ValueError('DB Type not in MySQL, Postgres, Hive')

        if len(self.data) == 0:
            raise Exception("No Data Returned")
        self.save_to_mysql('table_%s_%s' % (self.query_id, self.query_hash))
        return self.data

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
        query_text = self.query_text.replace('%', '%%')  # SQLAlchemy Esc
        result = c.execute(query_text)
        df = pd.DataFrame(result.fetchall())

        if df.shape == (0, 0):
            raise Exception("No Data Returned by Query!")
        df.columns = result.keys()
        c.close()
        return df

    def get_cache_status(self):
        """
        Returns if query used cache
        """
        return self.cached

    def check_cache(self):
        """
        Checks to see if this query's cache matches
        another previous and fresh query_tags
        returns table name / False
        """
        QC = models.QueryCache.objects.filter(
            query_id=self.query_id,
            hash=self.query_hash).order_by('run_time').first()
        if QC is None:
            return False
        elif QC.is_expired():
            return False
        else:
            return QC.table_name

    def retrieve_cache(self, table_name):
        """
        sets self.data from the query's cache
        """
        engine = get_db_engine.get_db_engine()
        self.data = pd.read_sql_table(table_name, con=engine)
        return self.data


class Manipulate_Data(Run_Query):
    def numericalize_data_array(self):
        """
        Checks for numbers encoded as strings due to bad database encoding
        """
        def num(foo):
            try:
                return float(foo)
            except (ValueError, TypeError) as e:
                return foo
        new_data = [[num(foo) for foo in row] for row in self.data_array]
        self.data_array = new_data
        return self.data_array

    def pivot(self, null_fill=0):
        # use pandas TODO to make the pivot
        if len(set(self.data.columns)) != len(self.data.columns):
            raise ValueError("Two or more columns have the same name")
        df2 = pd.pivot_table(
            self.data, values=self.data.columns[2],
            index=self.data.columns[0],
            columns=self.data.columns[1]).fillna(null_fill)
        df2.reset_index(level=0, inplace=True)
        self.data = df2
        return self.data

    def cumulative(self, axis=None, percent=None, relative_to=None):
        """
        TODO Make this actually do cumulative statistics
        """
        self.data = self.data[self.data.columns[1:]].cumsum()

    def rotate(self):
        """
        transpose data
        """
        self.data = self.data.transpose()

    def pandas_to_array(self):
        # logging.warning(self.data)
        self.data_array = [self.data.columns]
        self.data_array += [[v for v in r[1]] for r in self.data.iterrows()]
        # logging.warning(self.data_array)
        return self.data_array

    def html_table(self):
        """
        Returns a Pandas HTML Array from the data DataFrame
        """
        return(self.data.to_html(index=False))

    def generate_image(self, file_output=None, width=400, height=300):
        """
        create a picture!
        """
        data = copy.deepcopy(self.data_array)
        columns = data.pop(0)
        graph_data = {
            'columns': columns,
            'data': data,
            'chart_type': self.query_model.chart_type,
            'graph_extra': self.query_model.graph_extra,
            'yAxis_log': self.query_model.log_scale_y,
            'stacked': self.query_model.stacked,
            'xAxis': '',
            'yAxis': '',
            'graph_extra': self.query_model.graph_extra,
            'title': self.query_model.title}
        static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'website/static'))
        # logging.warning(static_path)
        guid = str(uuid.uuid1())
        json_data_file = '//tmp/%s.json' % (guid)
        cli = """phantomjs %s/js/phantom_make_chart.js '%s' %s""" % (
            static_path,
            json.dumps(graph_data, cls=DateTimeEncoder),
            json_data_file)
        # print cli
        # logging.warning(cli)
        subprocess.call([cli], shell=True)
        # Transform JSON file into image using CLI and Phantom JS
        if file_output is None:
            output_image = '%sthumbnails/%s.png' % (settings.MEDIA_ROOT, self.query_id)
        else:
            output_image = file_output
        cli = """phantomjs %s/Highcharts-4.0.3/exporting-server/phantomjs/highcharts-convert.js -infile %s -outfile %s -scale 2.5 -width %s - height %s""" % (static_path, json_data_file, output_image, width, height)
        # print cli
        subprocess.call([cli], shell=True)
        return output_image

    def run_manipulations(self):
        """
        Gets Processing steps from DB and executes them in order
        """
        query = models.Query.objects.filter(id=self.query_id).first()

        if query.pivot_data is True:  # if exists_and_equals(d, 'pivot','True'):
            self.pivot()
        if query.cumulative is True:
            self.cumulative()

        self.pandas_to_array()
        self.numericalize_data_array()

        """if self.query_model.chart_type != 'None':
            # Run the graph in phantom JS
            self.generate_image(fileout)
            self.query_model.image = fileout
            self.query_model.save()
        """

def string_to_boolean(string='', default=False):
    """
    returns a boolean from a given string
    """
    if string in [True, False]:
        return string
    if string.lower() == 'false':
        return False
    elif string.lower() == 'true':
        return True
    else:
        return default
