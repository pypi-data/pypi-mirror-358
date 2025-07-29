from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.md")
with codecs.open(readme_path, encoding="utf-8") as fh:
    long_description = fh.read()
VERSION = '0.0.1'
DESCRIPTION = 'Continous Time-Series Clustering And Merging towards Sentiments (CT-SCAMS) is a Python package ddesigned to ensure robust generalization across time stamps for sentiment analysis in policy-related texts. '
LONG_DESCRIPTION = 'Accounts temporal dynamics of policy-related texts and evaluate them under realistic settings that mimic typical sentiment analysis scenarios in policy studies. Specifically, it leverages continuous time-series clustering to select data points for annotation based on temporal trends and subsequently apply advanced merging techniques to merge multiple models, each fine-tuned separately on data from distinct time intervals.'

# Setting up
setup(
    name="ctscams",
    version=VERSION,
    author="Charles Alba",
    author_email="alba@wustl.edu",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["matplotlib", "ruptures", "pandas", "tqdm", "torch", "transformers", "datasets", "scikit-learn", "numpy"],
    keywords=["sentiment analysis", "temporal", "policy text", "online text"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
