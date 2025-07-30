from setuptools import setup, find_packages

# Read in the README.md for long_description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="finance-automl",
    version="0.1.3",
    author="Advait Dharmadhikari",
    author_email="advaituni@gmail.com",
    description="AutoML framework for financial time-series with leakage prevention and finance-specific metrics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/advait27/finautoml",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "matplotlib>=3.0.0",
        "optuna>=3.0.0",
        "scikit-learn>=0.24.0",
        "packaging<24,>=16.8",
        "docutils<0.19,>=0.14",
    ],
)
