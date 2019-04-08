#! _*_ coding: utf-8 _*_

from setuptools import find_packages, setup

setup(
    name='baby',
    version='1.0.0',
    pacakges=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask'
    ]
)