from setuptools import setup, find_packages
import requests
import bs4
import click
import yaypp


setup(
    name="conventions",
    version="0.3.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "click",
        "yaypp>=0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "conventions=conventions.cli:main",
        ],
    },
    author="Henry Anderson",
    author_email="hwranderson@gmail.com",
    description="A CLI tool to search for conference talks",
    keywords="conference, search, cli",
    url="https://github.com/hwranderson/conventions",
    python_requires=">=3.6",
    test_suite="tests",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
    ],
) 