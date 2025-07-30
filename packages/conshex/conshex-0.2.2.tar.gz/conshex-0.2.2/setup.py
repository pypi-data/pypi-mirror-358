#!/usr/bin/env python
from setuptools import setup
from conshex.version import version_string

setup(
    name = "conshex",
    version = version_string,
    packages = [
        'conshex',
        'conshex.lib',
    ],
    license = "MIT",
    description = "A powerful declarative symmetric parser/builder for binary data with XML de- and encoding",
    long_description = open("README.rst").read(),
    platforms = ["POSIX", "Windows"],
    url = "http://conshex.readthedocs.org",
    project_urls = {
        "Source": "https://github.com/ev1313/conshex",
        "Documentation": "https://conshex.readthedocs.io/en/latest/",
        "Issues": "https://github.com/ev1313/conshex/issues",
    },
    author = "Tim Blume",
    author_email = "conshex@3nd.io",
    python_requires = ">=3.10",
    install_requires = [],
    extras_require = {
        "extras": [
            "enum34",
            "numpy",
            "arrow",
            "ruamel.yaml",
            "lz4",
            "cryptography"
        ],
    },
    keywords = [
        "conshex",
        "construct",
        "declarative",
        "data structure",
        "struct",
        "binary",
        "symmetric",
        "parser",
        "builder",
        "parsing",
        "building",
        "pack",
        "unpack",
        "packer",
        "unpacker",
        "xml"
    ],
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
