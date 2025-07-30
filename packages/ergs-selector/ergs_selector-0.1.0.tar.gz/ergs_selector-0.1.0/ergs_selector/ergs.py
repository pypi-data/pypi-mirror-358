import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class ERGSSelector(BaseEstimator, TransformerMixin):
    def __init__(self, top_k=10):
        self.top_k = top_k
        self.feature_scores_ = None
        self.selected_features_ = None

    def fit(self, X, y):
        scores = {}
        features = X.columns
        classes = np.unique(y)

        for feature in features:
            ranges = [(X[y == cls][feature].min(), X[y == cls][feature].max()) for cls in classes]
            overlap_sum = 0
            pairs = 0
            for i in range(len(ranges)):
                for j in range(i + 1, len(ranges)):
                    i_min, i_max = ranges[i]
                    j_min, j_max = ranges[j]
                    intersection = max(0, min(i_max, j_max) - max(i_min, j_min))
                    union = max(i_max, j_max) - min(i_min, j_min)
                    if union > 0:
                        overlap_sum += intersection / union
                        pairs += 1
            avg_overlap = overlap_sum / pairs if pairs else 0
            scores[feature] = 1 - avg_overlap

        self.feature_scores_ = pd.Series(scores).sort_values(ascending=False)
        self.selected_features_ = self.feature_scores_.head(self.top_k).index.tolist()
        return self

    def transform(self, X):
        return X[self.selected_features_]

    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)
