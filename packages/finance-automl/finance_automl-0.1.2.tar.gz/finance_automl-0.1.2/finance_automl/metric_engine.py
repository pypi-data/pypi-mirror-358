import numpy as np
import pandas as pd

class MetricEngine:
    """
    Compute finance-specific metrics: Sharpe, max drawdown, Sortino, hit-rate.
    """
    def __init__(self, returns: pd.Series):
        self.returns = returns.dropna()

    def sharpe(self, annual_factor: int = 252) -> float:
        mean = self.returns.mean() * annual_factor
        vol = self.returns.std() * np.sqrt(annual_factor)
        return mean / vol if vol != 0 else np.nan

    def max_drawdown(self) -> float:
        cum = (1 + self.returns).cumprod()
        peak = cum.cummax()
        drawdown = (cum - peak) / peak
        return drawdown.min()

    def sortino(self, annual_factor: int = 252) -> float:
        negative = self.returns[self.returns < 0]
        downside = np.sqrt((negative**2).mean()) * np.sqrt(annual_factor)
        return (self.returns.mean() * annual_factor) / downside if downside != 0 else np.nan

    def hit_rate(self) -> float:
        return (self.returns > 0).mean()
