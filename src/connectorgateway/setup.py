#!/usr/bin/env python

from codecs import open
from setuptools import setup, find_packages

try:
    from azure_bdist_wheel import cmdclass  # pylint: disable=unused-import
except ImportError:
    from distutils import log as logger
    logger.warn("Wheel is not available, disabling bdist_wheel hook")


VERSION = '0.1.0'

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
]

DEPENDENCIES = []

with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='connectorgateway',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools Connector Gateway Extension',
    author='Microsoft Corporation',
    author_email='azpycli@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/connectorgateway',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=['tests']),
    install_requires=DEPENDENCIES,
    package_data={'azext_connectorgateway': ['azext_metadata.json']},
)