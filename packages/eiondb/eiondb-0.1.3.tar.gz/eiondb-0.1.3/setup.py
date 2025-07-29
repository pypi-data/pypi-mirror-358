#!/usr/bin/env python3

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eiondb",
    version="0.1.3",
    author="Eion Team", 
    author_email="mingyouk@gmail.com",
    description="Python SDK for Eion - Shared memory storage and collaborative intelligence for AI agent systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eiondb/eion-sdk-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "PyYAML>=5.4.0",
        "psutil>=5.8.0",
    ],
    include_package_data=True,
    package_data={
        "eiondb": [
            "server/*",
        ],
    },
    entry_points={
        "console_scripts": [
            "eion=eiondb.cli:main",
        ],
    },
) 