from setuptools import setup, find_packages
import os

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

# Read long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="bitcoin-dca",
    version="1.1.0",  # Match APP_VERSION in main.py
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'btc-dca=bitcoin_dca.main:main',
        ],
    },
    author="Albert Garcia",
    author_email="obokaman@gmail.com",
    description="Advanced Bitcoin DCA analysis with machine learning predictions and strategy optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/obokaman-com/bitcoin-dca",
    project_urls={
        "Bug Reports": "https://github.com/obokaman-com/bitcoin-dca/issues",
        "Source": "https://github.com/obokaman-com/bitcoin-dca",
    },
    python_requires=">=3.8",
    keywords="bitcoin, cryptocurrency, dca, dollar-cost-averaging, investment, analysis, machine-learning, prediction",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: End Users/Desktop", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Environment :: Console",
    ],
    include_package_data=True,
)