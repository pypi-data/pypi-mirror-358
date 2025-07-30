import matplotlib.pyplot as plt
import pandas as pd

class ReportGen:
    """
    Generate P&L curves, drawdown tables, turnover vs returns.
    """
    def __init__(self, returns: pd.Series):
        self.returns = returns.dropna()
        self.cum_returns = (1 + self.returns).cumprod()

    def plot_pnl(self):
        plt.figure()
        plt.plot(self.cum_returns)
        plt.title("Cumulative PnL")
        plt.xlabel("Time")
        plt.ylabel("Returns")
        plt.show()

    def drawdown_table(self):
        peak = self.cum_returns.cummax()
        dd = (self.cum_returns - peak) / peak
        table = pd.DataFrame({
            "drawdown": dd,
            "peak_date": peak.idxmax()
        })
        return table[dd < 0]
