from unittest import TestCase
import ml.views
import pandas as pd
import sklearn
import numpy as np


class TestLinearRegression(TestCase):
    def ml_object(self):
        mli = ml.views.MachineLearning(
            request=None,
            query_id=1,
            target_column='a',
            model_type='linear'
        )
        n_samples = 1000

        X, y, coef = sklearn.datasets.make_regressioni(
            n_samples=n_samples, n_features=2,
            n_informative=1, noise=10,
            coef=True, random_state=0
        )
        X2 = np.random.choice(['yes', 'no'], n_samples)

        y = pd.DataFrame(y)
        X = pd.DataFrame(X)
        X2 = pd.DataFrame(X2)
        df = pd.concat([y, X, X2], axis=1)
        df.columns=['y', 'a', 'b', 'c']
        mli.data = dfi
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
