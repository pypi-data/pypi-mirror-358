import unittest
from finance_automl.datasplitter import DataSplitter

class TestDataSplitter(unittest.TestCase):
    def test_split(self):
        import pandas as pd
        splitter = DataSplitter()
        # Create dummy DataFrames for testing
        X = pd.DataFrame({'a': [1, 2, 3]})
        y = pd.Series([4, 5, 6], name='b')
        # Add assertions for split logic
        result = splitter.split(X, y)
        # Replace with appropriate assertions based on expected split output
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
