# -*- coding: utf-8 -*-
"""
Installs one command-line executable:

    - ocrd-import-mscoco
"""


import codecs

from setuptools import setup, find_packages

setup(
    name='ocrd_publaynet',
    version='0.1.0',
    description='convert PubLayNet data into METS/PAGE-XML',
    long_description=codecs.open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Robert Sachunsky',
    author_email='sachunsky@informatik.uni-leipzig.de',
    url='https://github.com/bertsky/ocrd_publaynet',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=open('requirements.txt').read().split('\n'),
    entry_points={
        'console_scripts': [
            'ocrd-import-mscoco=ocrd_publaynet.import_mscoco:convert'
            ]
    }
)
