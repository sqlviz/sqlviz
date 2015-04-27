from unittest import TestCase
import ml.views
import pandas as pd
from django.core.urlresolvers import reverse
# import logging
# import json


class TestLinearRegression(TestCase):
    def ml_object(self):
        mli = ml.views.MachineLearning(
            request=None,
            query_id=1,
            target_column='a',
            model_type='linear'
        )
        mli.data = pd.DataFrame(
            [
                {'a': 10, 'b': '2.0', 'c': 50, 'd': 'yes'},
                {'a': 0, 'b': '10.0', 'c': 20, 'd': 'no'}
            ])
        self.mli = mli
        return mli

    def test_ml_string(self):
        mli = self.ml_object()
        ml_string = mli.build_model_string()
        self.assertEqual(
            ml_string,
            "a ~ b + c + C(d)")

    def test_linear_model(self):
        mli = self.ml_object()
        ml_string = 'a ~ b + c + C(d)'
        data = mli.data
        output = mli.linear_regression(data, ml_string)
        ml_string_out = output['data']['model_form']
        self.assertEquals(ml_string_out, ml_string)


class TestLogisticRegression(TestCase):
    def test_logistic_model(self):
        pass


class TestAdHocModel(TestCase):
    def test_ad_hoc_model(self):
        pass
