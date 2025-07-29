#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="pycdn",
    version="1.0.2",
    author="Harshal More",
    author_email="harshalmore2468@gmail.com",
    description="Revolutionary Python package delivery via CDN with serverless execution and lazy loading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harshalmore31/pycdn",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "httpx>=0.25.0",
        "pydantic>=2.4.0",
        "typing-extensions>=4.8.0",
        "cloudpickle>=3.0.0",
        "importlib-metadata>=6.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.9.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.6.0",
            "pre-commit>=3.5.0",
        ],
        "examples": [
            "openai>=1.0.0",
            "numpy>=1.24.0",
            "pandas>=2.0.0",
            "matplotlib>=3.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pycdn=pycdn.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="cdn, package-management, lazy-loading, serverless, distributed-computing",
    project_urls={
        "Bug Reports": "https://github.com/harshalmore31/pycdn/issues",
        "Source": "https://github.com/harshalmore31/pycdn",
        "Documentation": "https://docs.pycdn.dev",
    },
) 