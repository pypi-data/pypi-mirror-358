#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ 'peewee~=3.14.4',
                 'psycopg2-binary~=2.9.3',
                 'boto3~=1.17.53',
                 'tabulate~=0.8.9',
                 'click',
                 'simplejson~=3.17.2',
                 'owlready2~=0.46',
                 'requests~=2.28.0',
                 'rdflib~=6.3.2'
                ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Justin Payne",
    author_email='justin.payne@fda.hhs.gov',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python model package for the CFSAN Datonius framework (we're probably not calling it that.)",
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='datonius',
    name='datonius',
    packages=find_packages(include=['datonius', 'datonius.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/crashfrog/datonius',
    version="2.3.3",
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'dtns=datonius.cli:cli'
        ]
    }
)
