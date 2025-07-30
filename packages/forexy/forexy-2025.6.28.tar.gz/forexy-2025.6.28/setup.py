#!/usr/bin/python3
from setuptools import setup
from codecs import open
from os import path

with open('readme.md', 'r', encoding='utf-8') as f:
    readme = f.read()


setup(
  name                          = 'forexy',
  version                       = '2025.06.28',
  license                       = 'MIT',
  description                   = 'EXFOR utility codes', 
  long_description              = readme,
  long_description_content_type = 'text/markdown',
  keywords                      = 'EXFOR JSON',

  author                        = 'Naohiko Otsuka',
  author_email                  = 'n.otsuka@iaea.org',
  url                           = 'https://nds.iaea.org/nrdc/',

  packages                      = ['forexy'],
  install_requires              = ['pylatexenc', 'pyspellchecker', 'requests'],
  package_data                  = {'' : 
                                    [
                                     'LICENSE',
                                     'dict_9132.json',
                                     'dict_arc_new.044',
                                     'dict_arc_sup.227',
                                     'iaea-nds-0244-rev202506.pdf',
                                     'nubase_4.mas20.txt'
                                    ]
                                  }
)

