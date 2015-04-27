from unittest import TestCase
import website.query
import pandas as pd
import json


class TestLimits(TestCase):
    def test_adding_simple_limits(self):
        query = website.query.Query(
            query_text="select * from some_table",
            db=1)
        query.add_limit()
        self.assertEqual(
            query.query_text,
            "select * from some_table limit 1000;")

    def test_semicolon_limits(self):
        query = website.query.Query(
            query_text="select * from some_table;",
            db=1)
        query.add_limit()
        self.assertEqual(
            query.query_text,
            "select * from some_table limit 1000;")

    def test_limit_already_exists(self):
        query = website.query.Query(
            query_text="select * from some_table limit 10",
            db=1)
        query.add_limit()
        self.assertEqual(
            query.query_text,
            "select * from some_table limit 10")

    def test_limit_semicolon_already_exists(self):
        query = website.query.Query(
            query_text="select * from some_table limit 10;",
            db=1)
        query.add_limit()
        self.assertEqual(
            query.query_text,
            "select * from some_table limit 10;")


class TestSafety(TestCase):
    def stop_words(self):
        base_query = "select * from some_table"
        stop_words = ['insert', 'delete', 'drop',
                      'truncate', 'alter', 'grant']
        for word in stop_words:
            query = website.query.Query(
                query_text="%s %s " % (word, base_query),
                db=1)
            self.assertRaises(TypeError, query.check_safety)


class TestManipulateData(TestCase):
    """def test_numericalize_data_array(self):
        md = website.query.ManipulateData(
            query_text='',
            db='')
        md.data_array = [['a', '3', '4.0', '2014-01-02']]
        return_array = md.numericalize_data_array()
        self.assertListEqual(return_array, [['a', 3, 4.0, '2014-01-02']])
    """

    def test_pivot(self):
        md = website.query.ManipulateData(
            query_text='',
            db='')
        test_data = {
            'col1': ['cat', 'dog', 'cat', 'bear'],
            'col2': ['summer', 'summer', 'winter', 'winter'],
            'val': [1, 2, 3, 4]}
        md.data = pd.DataFrame(test_data)
        return_data = json.loads(md.pivot().to_json())
        self.assertDictEqual(
            return_data,
            {
                "col1": {"0": "bear", "1": "cat", "2": "dog"},
                "summer": {"0": 0.0, "1": 1.0, "2": 2.0},
                "winter": {"0": 4.0, "1": 3.0, "2": 0.0}
            })
