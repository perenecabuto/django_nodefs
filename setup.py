# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

PROJECT_DIR = os.path.dirname(__file__)

setup(
    name='django_nodefs',
    version='0.6-beta',
    url='https://github.com/perenecabuto/django_nodefs.git',
    author="Felipe Ramos",
    author_email="perenecabuto@gmail.com",
    description="NodeFS django app",
    long_description=open(os.path.join(PROJECT_DIR, 'README.md')).read(),
    keywords="Django, Fuse, Python",
    license='BSD',
    platforms=['linux'],
    packages=find_packages(exclude=["tests/"]),
    include_package_data=True,
    #zip_safe=False,
    install_requires=['Django==1.4.2'],
    dependency_links=['git+git://github.com/perenecabuto/nodefs.git#egg=nodefs'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)

