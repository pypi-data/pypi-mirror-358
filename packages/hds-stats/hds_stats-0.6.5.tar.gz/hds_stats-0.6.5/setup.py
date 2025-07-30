from setuptools import setup
from setuptools import find_packages

with open(file = 'README.md', mode = 'r', encoding = 'UTF-8') as file:
    long_description = file.read()

setup(
    name = 'hds-stats',
    version = '0.6.5',
    author = 'HelloDataScience',
    author_email = 'hellodatasciencekorea@gmail.com',
    
    description = 'Useful functions for EDA, Statistics and Machine Learning',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    
    url = 'https://github.com/HelloDataScience/hds-stats',
    project_urls = {
        'Bug Tracker': 'https://github.com/HelloDataScience/hds-stats/issues',
    },
    license = 'MIT',
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    
    python_requires = '>=3.12',
    packages = find_packages(),
    package_dir = {'hds_stats': 'hds_stats'},
    py_modules = ['stat', 'plot'],
    install_requires = [
        'numpy', 
        'pandas', 
        'scipy', 
        'seaborn', 
        'matplotlib', 
        'statsmodels', 
        'scikit-learn', 
        'graphviz', 
        'requests', 
        'bs4'
    ],
)