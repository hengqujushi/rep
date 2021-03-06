from __future__ import division, print_function, absolute_import

import numpy
import pandas
from scipy.special import expit, logit

from sklearn.utils.validation import column_or_1d
from ..utils import check_sample_weight, get_columns_in_df


__author__ = 'Alex Rogozhnikov'


def check_inputs(X, y, sample_weight, allow_none_weights=True):
    y = column_or_1d(y)
    if allow_none_weights and sample_weight is None:
        # checking only X, y
        if len(X) != len(y):
            raise ValueError('Different size of X: {} and y: {}'.format(X.shape, y.shape))
        return X, y, None

    if sample_weight is None:
        sample_weight = numpy.ones(len(y), dtype=float)

    sample_weight = column_or_1d(sample_weight)
    assert sum(numpy.isnan(sample_weight)) == 0, "Weight contains nan, this format isn't supported"
    if not (len(X) == len(y) == len(sample_weight)):
        message = 'Different sizes of X: {}, y: {} and sample_weight: {}'
        raise ValueError(message.format(X.shape, y.shape, sample_weight.shape))

    return X, y, sample_weight


def score_to_proba(score):
    proba = numpy.zeros([len(score), 2])
    proba[:, 1] = expit(score)
    proba[:, 0] = 1 - proba[:, 1]
    return proba


def proba_to_two_dimension(probability):
    proba = numpy.zeros([len(probability), 2])
    proba[:, 1] = probability
    proba[:, 0] = 1 - proba[:, 1]
    return proba


def proba_to_score(proba):
    assert proba.shape[1] == 2, 'Converting proba to score is possible only for two-class classification'
    proba = proba / proba.sum(axis=1, keepdims=True)
    score = logit(proba[:, 1])
    return score


def normalize_weights(y, sample_weight, per_class=True):
    """Returns normalized weights. Mean = 1.

    :param y: answers
    :param sample_weight: original weights (can not be None)
    :param per_class: if True
    """
    sample_weight = check_sample_weight(y, sample_weight=sample_weight)
    if per_class:
        sample_weight = sample_weight.copy()
        for label in numpy.unique(y):
            sample_weight[y == label] /= numpy.mean(sample_weight[y == label])
        return sample_weight
    else:
        return sample_weight / numpy.mean(sample_weight)


def _get_train_features(estimator, X, allow_nans=False):
        """
        :param pandas.DataFrame X: train dataset
        :param estimator: classifier or regressor
        :type estimator: Classifier or Regressor

        :return: pandas.DataFrame with used features
        """
        if isinstance(X, numpy.ndarray):
            X = pandas.DataFrame(X, columns=['Feature_%d' % index for index in range(X.shape[1])])
        else:
            assert isinstance(X, pandas.DataFrame), 'Support only numpy.ndarray and pandas.DataFrame'
        if estimator.features is None:
            estimator.features = list(X.columns)
            X_features = X
        elif list(X.columns) == list(estimator.features):
            X_features = X
        else:
            # assert set(self.features).issubset(set(X.columns)), "Data doesn't contain all training features"
            # X_features = X.ix[:, self.features]
            X_features = get_columns_in_df(X, estimator.features)

        if not allow_nans:
            # do by column to not create copy of all data frame
            for column in X_features.columns:
                assert numpy.all(numpy.isfinite(X_features[column])), "Does not support NaN: " + str(column)
        return X_features


