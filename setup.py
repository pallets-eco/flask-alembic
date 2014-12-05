#!/usr/bin/env python
import os
import re
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'flask_alembic', '__init__.py')) as f:
    version = re.search(r"__version__ = '(.*)'", f.read()).group(1)

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='Flask-Alembic',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='https://bitbucket.org/davidism/flask-alembic',
    license='BSD',
    author='David Lord',
    author_email='davidism@gmail.com',
    description='Flask extension to integrate Alembic migrations',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
    ],
    install_requires=requirements,
)
