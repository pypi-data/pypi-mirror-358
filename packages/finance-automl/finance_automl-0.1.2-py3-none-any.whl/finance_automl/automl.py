from .datasplitter import DataSplitter
from .metric_engine import MetricEngine
from .hyperoptimizer import HyperOptimizer
from .ensembler import Ensembler
from .reportgen import ReportGen
import pandas as pd


class AutoML:
    """
    Orchestrator: split → optimize → evaluate → ensemble → report → deploy
    """
    def __init__(self,
                 splitter: DataSplitter,
                 metric_name: str,
                 model_cls,
                 param_space,
                 n_trials: int = 50):
        self.splitter = splitter
        self.metric_name = metric_name
        self.model_cls = model_cls
        self.param_space = param_space
        self.n_trials = n_trials
        self.best_model = None

    def fit(self, X, y):
        for X_train, y_train, X_test, y_test in self.splitter.split(X, y):
            metric_func = lambda m: getattr(MetricEngine(m.fit(X_train, y_train).predict(X_test) - y_test), self.metric_name)()
            opt = HyperOptimizer(self.model_cls, self.param_space, metric_func, n_trials=self.n_trials)
            best_params = opt.optimize()
            model = self.model_cls(**best_params).fit(X_train, y_train)
            self.best_model = model
            self.reports = ReportGen(pd.Series(model.predict(X_test) - y_test))
            break  # only first fold for MVP
        return self

    def plot(self):
        self.reports.plot_pnl()

    def best_pipeline(self):
        return self.best_model
