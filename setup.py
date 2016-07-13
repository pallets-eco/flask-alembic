#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='Flask-Alembic',
    version='2.0.0',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Database :: Front-Ends',
    ],
    install_requires=[
        'alembic>=0.8',
        'Flask>=0.10',
        'Flask-SQLAlchemy',
        'SQLAlchemy'
    ],
)
