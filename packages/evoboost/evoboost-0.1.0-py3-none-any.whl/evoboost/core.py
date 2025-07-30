import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.tree import DecisionTreeRegressor
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import check_classification_targets
from scipy.special import softmax
from sklearn.metrics import log_loss, mean_squared_error


class EvoBoostClassifier(BaseEstimator, ClassifierMixin):
    """
    EvoBoost: Gradient boosting classifier using regression trees for residuals.
    """

    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3,
                 early_stopping_rounds=None, random_state=None):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.early_stopping_rounds = early_stopping_rounds
        self.random_state = random_state

    def fit(self, X, y, eval_set=None, verbose=False):
        X, y = check_X_y(X, y)
        check_classification_targets(y)

        if self.random_state is not None:
            np.random.seed(self.random_state)

        self.classes_ = np.unique(y)
        self.n_classes_ = len(self.classes_)

        # Convert y to one-hot encoding
        y_indices = np.searchsorted(self.classes_, y)
        y_onehot = np.zeros((len(y), self.n_classes_))
        y_onehot[np.arange(len(y)), y_indices] = 1

        y_pred = np.zeros_like(y_onehot)  # raw scores (logits)

        self.estimators_ = []  # list of lists of trees, one tree per class per iteration
        best_loss = float('inf')
        no_improvement = 0

        for i in range(self.n_estimators):
            proba = softmax(y_pred, axis=1)
            residual = y_onehot - proba

            trees = []
            update = np.zeros_like(y_pred)

            # Fit one regression tree per class
            for c in range(self.n_classes_):
                tree = DecisionTreeRegressor(
                    max_depth=self.max_depth,
                    random_state=self.random_state
                )
                tree.fit(X, residual[:, c])
                update[:, c] = tree.predict(X)
                trees.append(tree)

            self.estimators_.append(trees)
            y_pred += self.learning_rate * update

            # Early stopping with validation set
            if self.early_stopping_rounds and eval_set:
                X_val, y_val = eval_set
                val_pred = self.predict_proba(X_val)
                y_val_indices = np.searchsorted(self.classes_, y_val)
                y_val_onehot = np.zeros((len(y_val), self.n_classes_))
                y_val_onehot[np.arange(len(y_val)), y_val_indices] = 1

                loss = log_loss(y_val_onehot, val_pred)

                if verbose:
                    print(f"Iteration {i+1}, Validation Log Loss: {loss:.5f}")

                if loss < best_loss:
                    best_loss = loss
                    no_improvement = 0
                else:
                    no_improvement += 1
                    if no_improvement >= self.early_stopping_rounds:
                        if verbose:
                            print(f"Early stopping at iteration {i+1}")
                        break

        return self

    def predict_proba(self, X):
        check_is_fitted(self)
        X = check_array(X)

        y_pred = np.zeros((X.shape[0], self.n_classes_))
        for trees in self.estimators_:
            update = np.zeros_like(y_pred)
            for c, tree in enumerate(trees):
                update[:, c] = tree.predict(X)
            y_pred += self.learning_rate * update

        return softmax(y_pred, axis=1)

    def predict(self, X):
        proba = self.predict_proba(X)
        return self.classes_[np.argmax(proba, axis=1)]


class EvoBoostRegressor(BaseEstimator, RegressorMixin):
    """
    EvoBoost Regressor - Gradient boosting regressor using regression trees.
    """

    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3,
                 early_stopping_rounds=None, random_state=None):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.early_stopping_rounds = early_stopping_rounds
        self.random_state = random_state

    def fit(self, X, y, eval_set=None, verbose=False):
        X, y = check_X_y(X, y)

        if self.random_state is not None:
            np.random.seed(self.random_state)

        self.estimators_ = []
        self.baseline_pred_ = np.mean(y)
        y_pred = np.full_like(y, self.baseline_pred_, dtype=np.float64)

        best_loss = float('inf')
        no_improvement = 0

        for i in range(self.n_estimators):
            residual = y - y_pred

            tree = DecisionTreeRegressor(
                max_depth=self.max_depth,
                random_state=self.random_state
            )
            tree.fit(X, residual)
            self.estimators_.append(tree)

            update = tree.predict(X)
            y_pred += self.learning_rate * update

            if self.early_stopping_rounds and eval_set:
                X_val, y_val = eval_set
                val_pred = self.predict(X_val)
                loss = mean_squared_error(y_val, val_pred)

                if verbose:
                    print(f"Iteration {i+1}, Validation MSE: {loss:.5f}")

                if loss < best_loss:
                    best_loss = loss
                    no_improvement = 0
                else:
                    no_improvement += 1
                    if no_improvement >= self.early_stopping_rounds:
                        if verbose:
                            print(f"Early stopping at iteration {i+1}")
                        break

        return self

    def predict(self, X):
        check_is_fitted(self)
        X = check_array(X)

        pred = np.full(X.shape[0], self.baseline_pred_, dtype=np.float64)
        for tree in self.estimators_:
            pred += self.learning_rate * tree.predict(X)

        return pred

    def get_feature_importances(self):
        check_is_fitted(self)
        importances = np.zeros(len(self.estimators_[0].feature_importances_))
        for tree in self.estimators_:
            importances += tree.feature_importances_
        return importances / len(self.estimators_)
