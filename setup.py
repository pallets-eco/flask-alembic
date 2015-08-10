#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='Flask-Alembic',
    version='1.1.2',
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
    install_requires=[
        'alembic>=0.7',
        'Flask>=0.10',
        'Flask-SQLAlchemy>=2',
        'SQLAlchemy>=0.9'
    ],
)
