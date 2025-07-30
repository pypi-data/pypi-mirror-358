#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import cfglog  # noqa: F401

setup(
    name='cfglog',
    version='1.0.0',
    description='Configure Logging Easily',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Zhiqing Xiao',
    author_email='xzq.xiaozhiqing@gmail.com',
    url='http://github.com/cfglog/cfglog',
    py_modules=["cfglog"],
    include_package_data=True,
    license="MIT",
    classifiers=[
        'Programming Language :: Python',
    ],
)
