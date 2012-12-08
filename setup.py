# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

PROJECT_DIR = os.path.dirname(__file__)

setup(
    name='django_nodefs',
    version='0.3-beta',
    url='https://github.com/perenecabuto/django_nodefs.git',
    author="Felipe Ramos",
    author_email="perenecabuto@gmail.com",
    description="NodeFS django app",
    long_description=open(os.path.join(PROJECT_DIR, 'README.md')).read(),
    keywords="Django, Fuse, Python",
    license='BSD',
    platforms=['linux'],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=open(os.path.join(PROJECT_DIR, 'requirements.txt')).read().splitlines(),
    #classifiers=[]
)

