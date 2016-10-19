import os
import re
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'jsondiff', '__init__.py')) as f:
    version = re.compile(r".*__version__ = '(.*?)'", re.S).match(f.read()).group(1)

setup(
    name='jsondiff',
    packages=find_packages(),
    version=version,
    description='Diff JSON and JSON-like structures in Python',
    author='Zoomer Analytics LLC',
    author_email='eric.reynolds@zoomeranalytics.com',
    url='https://github.com/ZoomerAnalytics/jsondiff',
    keywords=['json', 'diff', 'diffing', 'difference', 'patch', 'delta', 'dict', 'LCS'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
)
