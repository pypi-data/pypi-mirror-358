from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="jbridgedf",
    version="0.1.3",
    description="Bridge JSON APIs into clean, time-aware DataFrames.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Luis Felipe de Moraes",
    author_email="luis.felipe@email.com",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "requests>=2.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.8',
)
