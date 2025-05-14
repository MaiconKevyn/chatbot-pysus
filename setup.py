# setup.py na raiz do projeto
from setuptools import setup, find_packages

setup(
    name="chatbot-pysus",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pandas"

    ],
)
