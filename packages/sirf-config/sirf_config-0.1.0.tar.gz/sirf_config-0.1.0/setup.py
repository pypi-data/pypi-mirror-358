#!/usr/bin/env python3
"""
Setup script for sirf-config package.
This is a fallback for older Python/pip versions that don't support pyproject.toml.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from __init__.py
def get_version():
    version_file = os.path.join(here, 'src', 'sirf_config', '__init__.py')
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('"')[1]
    raise RuntimeError('Version not found')

setup(
    name='sirf-config',
    version=get_version(),
    description='Configuration management for SIRF SPECT/PET reconstruction workflows',
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/sirf-config',
    
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    # Include package data
    package_data={
        'sirf_config': ['default_configs/*.yaml'],
    },
    
    python_requires='>=3.8',
    install_requires=[
        'pyyaml>=6.0',
        'typing-extensions>=4.0.0; python_version<"3.10"',
    ],
    
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
            'black>=22.0',
            'flake8>=5.0',
            'isort>=5.0',
            'mypy>=1.0',
        ],
        'docs': [
            'sphinx>=5.0',
            'sphinx-rtd-theme>=1.0',
            'myst-parser>=0.18',
        ],
        'examples': [
            'matplotlib>=3.5',
            'numpy>=1.20',
        ],
    },
    
    entry_points={
        'console_scripts': [
            'sirf-config=sirf_config.cli:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    
    keywords='SIRF SPECT PET medical imaging reconstruction configuration',
    
    project_urls={
        'Documentation': 'https://sirf-config.readthedocs.io',
        'Source': 'https://github.com/yourusername/sirf-config',
        'Tracker': 'https://github.com/yourusername/sirf-config/issues',
    },
)