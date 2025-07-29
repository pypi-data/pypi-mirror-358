import os
from setuptools import setup, find_packages

setup(
    name="traffic-aware-route-optimizer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "googlemaps>=4.10.0",
        "httpx>=0.24.0",
    ],
    python_requires=">=3.8",
    author="Luis Ticas",
    author_email="luis.ticas1@gmail.com",
    description="Traffic-aware route optimization using Google Routes API",
    long_description=open("README.md", "r", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)