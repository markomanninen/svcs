#!/usr/bin/env python3
"""
SVCS Setup Script

This script installs SVCS globally so users can simply run:
  svcs init
in any repository and it works.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="svcs",
    version="0.1",
    description="Semantic Version Control System - Repository-local git-integrated semantic analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SVCS Team",
    author_email="contact@svcs.dev",
    url="https://github.com/svcs/svcs",
    license="MIT",
    
    packages=find_packages(),
    
    # Include package data
    package_data={
        'svcs': [
            'analyzer.py',
            '*.py',
        ],
    },
    
    # Install requirements
    install_requires=[
        # Core and AI dependencies
        'rich>=12.0.0',
        'google-generativeai>=0.3.0',
        'tenacity>=8.0.0',
        # Language parsers
        'esprima>=4.0.1',
        'phply>=1.2.6',
        'tree-sitter>=0.20.0',
        'tree-sitter-php>=0.20.0',
    ],
    
    # Console scripts - this makes 'svcs' command available globally
    entry_points={
        'console_scripts': [
            'svcs=svcs.__main__:main',
        ],
    },
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
    # Keywords for PyPI search
    keywords='version-control semantic-analysis git development-tools',
    
    # Additional metadata
    project_urls={
        'Bug Reports': 'https://github.com/svcs/svcs/issues',
        'Source': 'https://github.com/svcs/svcs',
        'Documentation': 'https://github.com/svcs/svcs/docs',
    },
)
