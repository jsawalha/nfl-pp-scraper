from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'A basic package to execute web scraping from www.playerprofiler.com'

# Setting up
setup(
    name="autotraderprojectjeff",
    version=VERSION,
    author="Jeff Sawalha",
    author_email="<jsawalha@ualberta.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['beautifulsoup4', 'scikit-learn'],
    keywords=['python', 'machine learning', 'project'],
)