"""Evaluation functions and helper functions for the Gaussian process model"""
import logging

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.exceptions import ConvergenceWarning
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import cross_validate
from sklearn.utils._testing import ignore_warnings

from .numeric_transformers import MyLogTransformer
from .transformed_target_regressor_with_uncertainty import TransformedTargetRegressorWithUncertainty

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# centers data to a zero mean
# use this transformer if you want to center the data outside of the GP model (e.g. for visualization)
class TargetTransformer(TransformerMixin, BaseEstimator):
    def __init__(self, function=(lambda y: y), inverse_function=(lambda y: y)):
        self.function = function
        self.inverse_function = inverse_function
        self.mean = 0

    def fit(self, y):
        self.targets = y
        self.mean = np.mean(self.function(y))

    def transform(self, y):
        return self.function(y) - self.mean

    def inverse_transform(self, y):
        return self.inverse_function(y + self.mean)

    def fit_transform(self, y):
        self.fit(y)
        return self.transform(y)


def evaluate(model, train, validation, features:list[str]=None):
    """Evaluate the model on the training and validation set.

    Args:
        feature(list[str]): list of features to be used for the model, default is ["lon", "lat"]
    """
    if features is None:
        features = ["lon", "lat"]
    train["pred"] = model.predict(train[features].values)

    logger.info(f"Training RMSE: {root_mean_squared_error(train['wait'], train['pred'])}")
    logger.info(f"Training MAE {mean_absolute_error(train['wait'], train['pred'])}")

    validation["pred"] = model.predict(validation[features].values)

    logger.info(
        f"Validation RMSE: {root_mean_squared_error(validation['wait'], validation['pred'])}"
    )
    logger.info(
        f"Validation MAE {mean_absolute_error(validation['wait'], validation['pred'])}\n"
    )


@ignore_warnings(category=ConvergenceWarning)
def evaluate_cv(estimator, X, y, folds=5):
    cv_result = cross_validate(
        estimator=estimator,
        X=X,
        y=y,
        cv=folds,
        scoring=["neg_mean_absolute_error", "neg_root_mean_squared_error"],
        return_train_score=True,
        return_estimator=True,
    )

    logger.info("Cross-validated averaged metrics...")
    logger.info(
        f"Training RMSE: {cv_result['train_neg_root_mean_squared_error'].mean() * -1}"
    )
    logger.info(f"Training MAE: {cv_result['train_neg_mean_absolute_error'].mean() * -1}")
    logger.info(
        f"Validation RMSE: {cv_result['test_neg_root_mean_squared_error'].mean() * -1}"
    )
    logger.info(f"Validation MAE: {cv_result['test_neg_mean_absolute_error'].mean() * -1}\n")

    # returning one estimators trained on all samples for visualization purposes
    return estimator.fit(X, y)


def get_gpr(initial_kernel, train_from_scrath: bool = True):
    optimizer = "fmin_l_bfgs_b" if train_from_scrath else None
    gpr = GaussianProcessRegressor(
        kernel=initial_kernel,
        alpha=0.0**2,
        optimizer=optimizer,
        normalize_y=True,
        n_restarts_optimizer=0,
        random_state=42,
    )

    target_transform_gpr = TransformedTargetRegressorWithUncertainty(
        regressor=gpr, numeric_transformer=MyLogTransformer()
    )

    return target_transform_gpr


def fit_gpr(gpr, X, y):
    gpr.fit(X, y)

    return gpr


@ignore_warnings(category=ConvergenceWarning)
def fit_gpr_silent(gpr, X, y):
    logger.info(f"Fitting Gaussian Process Regressor with X of shape {X.shape} and y of shape {y.shape}...")
    gpr.fit(X, y)
    logger.info("Fitting done.")

    return gpr


def get_optimized_gpr(initial_kernel, X, y, train_from_scratch: bool=True, verbose : bool=False):
    gpr = get_gpr(initial_kernel=initial_kernel, train_from_scrath=train_from_scratch)
    gpr = fit_gpr(gpr, X, y) if verbose else fit_gpr_silent(gpr, X, y)

    return gpr
