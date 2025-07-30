import numpy
import warnings
from sklearn.base import BaseEstimator
from sklearn.exceptions import DataConversionWarning
from sklearn.utils.estimator_checks import check_supervised_y_2d
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris

class RoundRobinClassifier(BaseEstimator):
    def __init__(self, random_state=0):
        self.random_state = random_state


    def fit(self, X, y):
        if len(y.shape[1:]) >= 1:
            warnings.warn(
                    'A column-vector y was passed when a 1d array was expected',
                    DataConversionWarning)
        if not hasattr(self, 'idx'):
            self.idx = int(self.random_state)
        self.classes_ = numpy.unique(y)
        return self


    def predict(self, X):
        pred = []
        for i, _ in enumerate(X):
            pred.append(self.classes_[self.idx % len(self.classes_)])
            self.idx = (self.idx + 1) % len(self.classes_)
        return numpy.asarray(pred)


classif = RoundRobinClassifier()
check_supervised_y_2d(classif.__class__.__name__, classif)

estimator_list = [RandomForestClassifier, ]
data, labels = load_iris()

for Estimator in estimator_list:  # various estimators to be checked
    est1 = Estimator()
    est1.fit(data, labels)
    est2 = Estimator()
    est2.fit(data, labels)
    if not check_identical(est1, est2):
        raise EstimatorFitError('blah')