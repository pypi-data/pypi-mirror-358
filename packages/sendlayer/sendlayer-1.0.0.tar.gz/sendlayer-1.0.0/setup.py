from setuptools import setup, find_packages
import os
import re


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sendlayer",
    # version is dynamically set by pyproject.toml
    author="SendLayer",
    author_email="support@sendlayer.com",
    maintainer="David Ozokoye",
    description="Official Python SDK for SendLayer API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sendlayer/sendlayer-python",
    packages=find_packages(where="src"),
    keywords=["email", "sendlayer", "sdk", "api", "transactional email", "mail", "send email", "email api", "sendlayer api", "send email python", "python email package"],
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ]
) 