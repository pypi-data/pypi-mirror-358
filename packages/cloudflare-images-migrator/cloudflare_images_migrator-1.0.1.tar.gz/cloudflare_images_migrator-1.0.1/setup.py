#!/usr/bin/env python3
"""
Setup configuration for Cloudflare Images Migration Tool
Enterprise-grade image migration with persistent tracking and duplicate detection
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cloudflare-images-migrator",
    version="1.0.1",
    author="Mario Lemos Quirino Neto",
    author_email="mariolqn@users.noreply.github.com",
    description="Enterprise-grade tool to migrate images to Cloudflare Images with persistent tracking and duplicate detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mariolqn/Cloudflare-Images-Migrator",
    project_urls={
        "Bug Tracker": "https://github.com/mariolqn/Cloudflare-Images-Migrator/issues",
        "Documentation": "https://github.com/mariolqn/Cloudflare-Images-Migrator#readme",
        "Source Code": "https://github.com/mariolqn/Cloudflare-Images-Migrator",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Backup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "cloudflare-images-migrator=main:main",
            "cf-images-migrate=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.txt", "*.md"],
    },
    keywords=[
        "cloudflare",
        "images",
        "migration",
        "cdn",
        "optimization",
        "duplicate-detection",
        "enterprise",
        "security",
        "tracking",
        "automation",
    ],
    zip_safe=False,
) 