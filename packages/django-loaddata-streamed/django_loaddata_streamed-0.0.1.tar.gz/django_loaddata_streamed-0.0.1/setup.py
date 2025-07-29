#!/usr/bin/python

"""
A setuptools based setup module.
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
from loaddata_streamed import __version__ as version

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='django-loaddata-streamed',

    version=version,
    python_requires='>=3.8',

    description='Django-Loaddata-Streamed - streaming JSON fixtures to make loaddata less memory-consuming',
    long_description=long_description,

    url='https://github.com/nnseva/django-loaddata-streamed',

    author='Vsevolod Novikov',
    author_email='nnseva@gmail.com',

    zip_safe=False,
    platforms="any",

    license='LGPL',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        'Environment :: Web Environment',

        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',

        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],

    keywords='django loaddata json stream streaming',
    packages=find_packages(exclude=['dev']),
    install_requires=['django>=2.2', 'json_stream'],
)
