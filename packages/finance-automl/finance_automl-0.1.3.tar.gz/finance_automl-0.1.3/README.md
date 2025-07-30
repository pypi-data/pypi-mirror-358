### README.md
```markdown
# finance_automl

**finance_automl** is an end-to-end AutoML framework tailored specifically for financial time-series forecasting and backtesting. It combines robust leakage prevention, finance-native metrics, and seamless deployment hooks into a single, easy-to-use Python package.

## Project Description
Financial machine learning projects face unique challenges—rolling-window data splits, lookahead bias, non-standard evaluation metrics, and complex backtesting requirements. **finance_automl** addresses these pain points by providing:

- **Leakage-Proof Data Splitting**: Enforced rolling or expanding window splits with configurable purge gaps to eliminate lookahead bias.
- **Finance-Centric Metrics**: Built-in support for Sharpe ratio, max drawdown, Sortino ratio, and hit-rate, enabling model tuning on real-world performance measures.
- **Automated Hyperparameter Optimization**: Seamless integration with Optuna, optimized over chosen finance KPIs for robust model selection.
- **Ensembling with Weighted Blends**: Simple stacking ensemble that adaptively weights base models based on cross-period consistency.
- **Automated Reporting**: Generate P&L curves, drawdown tables, and portfolio turnover analysis with a single function call.
- **One-Click Deployment**: Docker exports and cron-based retrain scheduling to push your best model into production effortlessly.

## Key Features
1. **DataSplitter**: Rolling/expanding splits, purge gaps, and flexible train/test sizing.
2. **MetricEngine**: Sharpe, drawdown, Sortino, and hit-rate calculators.
3. **HyperOptimizer**: Optuna-driven search tuned to finance-specific objectives.
4. **Ensembler**: Stack and blend models with finance-aware weight assignment.
5. **ReportGen**: Auto-generate performance reports, charts, and tables.
6. **DeployHook**: Build Docker images and schedule retraining jobs via cron.

## Installation
```bash
pip install finance-automl
```

## Quickstart
```python
from finance_automl import AutoML, DataSplitter
from sklearn.ensemble import RandomForestRegressor

# 1. Configure a rolling split with a 5-day purge gap
splitter = DataSplitter(window_type="rolling", lookback=252, gap=5, test_size=0.2)

# 2. Initialize AutoML with your model, hyperparameter space, and Sharpe objective
automl = AutoML(
    splitter=splitter,
    metric_name="sharpe",
    model_cls=RandomForestRegressor,
    param_space={"n_estimators": [100, 200], "max_depth": [5, 10]},
    n_trials=20
)

# 3. Fit on your dataset (X: features, y: target returns)
automl.fit(X, y)

# 4. Visualize cumulative P&L
automl.plot()
```

## License
MIT
```
