import unittest
import pandas as pd
from finance_automl.metric_engine import MetricEngine

class TestMetricEngine(unittest.TestCase):
    def test_evaluate(self):
        engine = MetricEngine(returns=None)
        # Add assertions for evaluate logic
        self.assertIsNone(engine.evaluate(None, None))

if __name__ == "__main__":
    unittest.main()
