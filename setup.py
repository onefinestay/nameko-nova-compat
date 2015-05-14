#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='nameko-nova-compat',
    version='0.0.2',
    description='Nova-RPC compatibility for nameko services',
    author='onefinestay',
    author_email='engineering@onefinestay.com',
    url='http://github.com/onefinestay/nameko-nova-compat',
    packages=find_packages(exclude=['test']),
    install_requires=[
        "nameko>=2.0.0",
        "iso8601"
    ],
    extras_require={
        'dev': [
            "coverage==4.0a1",
            "flake8==2.1.0",
            "mccabe==0.3",
            "pep8==1.6.1",
            "pyflakes==0.8.1",
            "pylint==1.0.0",
            "pytest==2.4.2",
            "pytest-timeout==0.4",
        ]
    },
    dependency_links=[],
    zip_safe=True,
    license='Apache License, Version 2.0',
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
