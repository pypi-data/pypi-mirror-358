from setuptools import setup, find_packages

setup(
    name="jbridgedf",
    version="0.1.0",
    description="Bridge JSON APIs into clean, time-aware DataFrames.",
    author="Luis Felipe de Moraes",
    author_email="luis.felipe@email.com",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "requests>=2.0.0"
    ],
    python_requires='>=3.8',
)