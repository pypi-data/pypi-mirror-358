from typing import Iterator, Tuple
import pandas as pd

class DataSplitter:
    """
    Rolling/expanding window splitter with purge gap to prevent leakage.
    """
    def __init__(self,
                 window_type: str = "rolling",
                 lookback: int = 252,
                 gap: int = 0,
                 test_size: float = 0.2):
        self.window_type = window_type
        self.lookback = lookback
        self.gap = gap
        self.test_size = test_size

    def split(self, X: pd.DataFrame, y: pd.Series) -> Iterator[Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]]:
        n = len(X)
        test_len = int(n * self.test_size) if isinstance(self.test_size, float) else int(self.test_size)
        start = 0
        while True:
            end_train = start + self.lookback
            start_test = end_train + self.gap
            end_test = start_test + test_len
            if end_test > n:
                break
            yield (X.iloc[start:end_train], y.iloc[start:end_train],
                   X.iloc[start_test:end_test], y.iloc[start_test:end_test])
            start = start + test_len if self.window_type == "rolling" else 0
