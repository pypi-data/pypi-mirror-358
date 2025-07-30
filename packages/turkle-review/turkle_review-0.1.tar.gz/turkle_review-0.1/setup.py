# setup.py
from setuptools import setup, find_packages

setup(
    name='turkle-review',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=4.2',
    ],
)

