from django.http import HttpResponse
# from django.shortcuts import render
# from sklearn import (metrics, linear_model, cross_validation)
import statsmodels.formula.api as smf
import statsmodels as sm
import models
import website.query as query
# from sklearn.metrics import roc_auc_scor
import json
import logging
import base64
import pickle


def build_model(request, ml_id):
    ml = MachineLearning(request, ml_id)
    return ml.build_model()


def use_model(request, ml_id):
    ml = MachineLearning(request, ml_id)
    x = json.loads(request.GET.get('data', None))
    return ml.use_model(x)


class MachineLearning:
    def __init__(self, request, ml_id):
        print('ml started')
        self.request = request
        self.ml_id = ml_id
        self.ml_model = models.machine_learning_model.objects.filter(id=ml_id).first()
        print self.ml_model
        self.model = None

    def build_model(self):
        # Build model and return results as API
        print(self.ml_model)
        if self.ml_model.type == 'logistic':
            return_data = self.logistic_regression()
        elif self.ml_model.type == 'linear':
            return_data = self.linear_regression()
        # save results if requested
        if True:
            self.model_to_db()
        # Return to API
        return return_data

    def use_model(self, x):
        # Find latest model
        self.db_to_model()
        return HttpResponse(json.dumps(self.apply_model(x).tolist()),
                            content_type="application/json")

    def prepare_data(self):
        ml_data = self.ml_model
        query_id = ml_data.query_id
        lq = query.LoadQuery(
            query_id=query_id,
            user=self.request.user,
            parameters=self.request.GET.dict(),
            cacheable=self.request.GET.get('cacheable', None)
        )
        q = lq.prepare_query()
        q.run_query()
        q.run_manipulations()
        self.data = q.return_data()
        return self.data

    def build_model_string(self):
        ml_string = []
        for col_name, col_type in (zip(self.data.columns, self.data.dtypes)):
            if col_name != self.ml_model.target_column:
                if col_type == 'object':
                    ml_string.append('C(%s)' % col_name)
                else:
                    ml_string.append(col_name)
        ml_string = ' + '.join(ml_string)
        ml_string = '%s ~ %s' % (self.ml_model.target_column, ml_string)
        return ml_string.encode("ascii")

    def linear_regression(self):
        self.prepare_data()
        ml_string = self.build_model_string()
        self.model = smf.ols(formula=ml_string, data=self.data).fit()
        self.model_to_db()
        params = self.model.params
        summary = str(self.model.summary())
        print summary
        return_data = {
            "data":
                {
                    "params": params.tolist(),
                    "summary": summary
                },
            "error": False}

        return HttpResponse(json.dumps(return_data),
                            content_type="application/json")

    def apply_model(self, x):
        return self.model.predict(x)

    def logistic_regression(self, test_size=.3, penalty='l2'):

        X, y = self.prepare_data()
        X_train, X_cv, y_train, y_cv = cross_validation.train_test_split(
                X, y, test_size=test_size)
        clf = linear_model.LogisticRegression(C=1.0, penalty=penalty, tol=1e-6)
        clf.fit(X_train, y_train)
        coeff = clf.coef_.tolist()
        intercept = clf.intercept_.tolist()

        # calculate AUC
        preds = clf.predict_proba(X_cv)[:, 1]
        fpr, tpr, thresholds = metrics.roc_curve(y_cv, preds)

        auc = metrics.auc(fpr, tpr)

        # Calculate Z scores :(
        # TODO

        return_data = {
            "data":
                {"coeff": coeff, "intercept": intercept, "auc": auc},
            "error": False}
        logging.warning(return_data)

        self.model = clf
        return HttpResponse(json.dumps(return_data),
                            content_type="application/json")

    def model_to_db(self):
        object2varchar = lambda obj: unicode(base64.b64encode(pickle.dumps(obj)))
        blob = object2varchar(self.model)
        qv = models.model_blob(model_id= self.ml_model, blob=blob)
        qv.save()

    def db_to_model(self):
        varchar2object = lambda obj: pickle.loads(unicode(base64.b64decode(obj)))
        blob = models.model_blob.objects.filter(model_id=self.ml_model).last().blob
        self.model = varchar2object(blob)
        return self.model
