#!/usr/bin/env python3
"""
Setup script for FCSP API library.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements if they exist
def read_requirements():
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        with open(requirements_file, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

setup(
    name="fcsp-api",
    version="0.1.1",
    author="Eric Pullen",
    author_email="eric@ericpullen.com",
    description="A Python library for interacting with Ford Charge Station Pro (FCSP) devices via their REST API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ericpullen/fcsp-api",
    project_urls={
        "Documentation": "https://github.com/ericpullen/fcsp-api#readme",
        "Repository": "https://github.com/ericpullen/fcsp-api.git",
        "Issues": "https://github.com/ericpullen/fcsp-api/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: System :: Hardware",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "twine>=3.0",
            "build>=0.10",
        ],
        "crypto": [
            "cryptography>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fcsp-scanner=fcsp_api.scanner:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 