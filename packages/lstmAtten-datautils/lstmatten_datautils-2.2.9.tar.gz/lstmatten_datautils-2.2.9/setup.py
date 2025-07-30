# lstmAtten_datautils/setup.py
from setuptools import setup, find_packages

setup(
    name="lstmAtten_datautils",
    version="2.2.9",
    author="DT.L",
    description="A utility package for processing data for LSTM Attention models in relation classification",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "torch>=1.7.0",
        "shutup>=0.2.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)