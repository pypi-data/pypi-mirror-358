from sklearn.base import BaseEstimator, RegressorMixin
import numpy as np
from typing import List, Optional

class Ensembler(BaseEstimator, RegressorMixin):
    """
    Simple stacking ensemble with finance-aware weighting.
    """
    def __init__(self, models: list, weights: Optional[List] = None):
        self.models = models
        self.weights = weights

    def fit(self, X, y):
        for m in self.models:
            m.fit(X, y)
        return self

    def predict(self, X):
        preds = np.column_stack([m.predict(X) for m in self.models])
        if self.weights is None:
            self.weights = np.ones(preds.shape[1]) / preds.shape[1]
        return preds.dot(self.weights)
