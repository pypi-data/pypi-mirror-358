from typing import Dict, Any
import optuna

class HyperOptimizer:
    """
    Optimize model hyperparameters via Optuna, using custom finance metrics.
    """
    def __init__(self, model_cls, param_space: Dict[str, Any], metric_func, n_trials: int = 50):
        self.model_cls = model_cls
        self.param_space = param_space
        self.metric_func = metric_func
        self.n_trials = n_trials
        self.study = None

    def _objective(self, trial):
        params = {k: trial.suggest_categorical(k, v) if isinstance(v, list)
                  else trial.suggest_float(k, v[0], v[1])
                  for k, v in self.param_space.items()}
        model = self.model_cls(**params)
        score = self.metric_func(model)
        return score

    def optimize(self):
        self.study = optuna.create_study(direction="maximize")
        self.study.optimize(self._objective, n_trials=self.n_trials)
        return self.study.best_params
