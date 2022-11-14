from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'A basic package to execute this project'
LONG_DESCRIPTION = 'A package that allows to scrape, proecessing and train samples from playerprofiler.com. This is to predict fantasy football output'

# Setting up
setup(
    name="autotraderprojectjeff",
    version=VERSION,
    author="Jeff Sawalha",
    author_email="<jsawalha@ualberta.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['beautifulsoup4', 'scikit-learn'],
    keywords=['python', 'machine learning', 'project'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Students",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)