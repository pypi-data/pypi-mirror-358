from setuptools import setup, find_packages

setup(
    name="finance_automl",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "pandas", "numpy", "matplotlib", "optuna", "scikit-learn"
    ],
    python_requires=">=3.9",
    author="Your Name",
    description="AutoML framework for financial time-series with leakage prevention and finance-specific metrics.",
    url="https://github.com/advait27/finautoml"
)
