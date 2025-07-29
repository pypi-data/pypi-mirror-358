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
    version="1.1.6",
    author="Harshal More",
    author_email="harshalmore2468@gmail.com",
    description="Revolutionary Package CDN with Natural Import System - Stream Python packages instantly without local installation!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harshalmore2268/pycdn",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Software Distribution",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn[standard]>=0.15.0", 
        "requests>=2.25.1",
        "pydantic>=1.8.0",
        "websockets>=10.0",
        "cryptography>=41.0.0",
        "python-dotenv>=1.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "httpx>=0.23.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "flake8>=3.9.0",
        ],
        "server": [
            "gunicorn>=20.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pycdn=pycdn.cli:main",
        ],
    },
    keywords=["cdn", "package-management", "lazy-loading", "serverless", "distributed-computing"],
    project_urls={
        "Bug Reports": "https://github.com/harshalmore2268/pycdn/issues",
        "Source": "https://github.com/harshalmore2268/pycdn",
        "Documentation": "https://github.com/harshalmore2268/pycdn#readme",
    },
    include_package_data=True,
    zip_safe=False,
) 