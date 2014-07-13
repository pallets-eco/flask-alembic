#!/usr/bin/env python
from setuptools import setup

setup(
    name='Flask-Alembic',
    version='1.0.1',
    description='Flask extension to integrate Alembic migrations',
    author='David Lord',
    author_email='davidism@gmail.com',
    url='https://bitbucket.org/davidism/flask-alembic',
    license='BSD',
    zip_safe=False,
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
    packages=[
        'flask_alembic',
        'flask_alembic.cli'
    ],
    install_requires=[
        'alembic>=0.6.5',
        'Flask>=0.10.1',
        'Flask-SQLAlchemy>=1.0',
        'SQLAlchemy>=0.9.4',
    ],
)
