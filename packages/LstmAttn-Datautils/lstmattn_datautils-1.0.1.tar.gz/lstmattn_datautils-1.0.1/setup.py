# lstmAtten_datautils/setup.py
from setuptools import setup, find_packages

setup(
    name="LstmAttn_Datautils",
    version="2.2.2",
    author="WX.W",
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
