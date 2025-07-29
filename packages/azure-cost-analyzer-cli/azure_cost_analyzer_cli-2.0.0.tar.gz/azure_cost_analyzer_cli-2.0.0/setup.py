"""
Setup configuration for Azure Cost Analyzer CLI package.
"""

from setuptools import setup
import os

# Read the README file
def read_long_description():
    """Read the README.md file for long description."""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "Enterprise Azure cost analysis tool with comprehensive reporting capabilities."

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt."""
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return ["pandas>=1.3.0", "matplotlib>=3.3.0", "openpyxl>=3.0.0", "seaborn>=0.11.0"]

# Package metadata
setup(
    name="azure-cost-analyzer-cli",
    version="2.0.0",
    author="Qanooni",
    author_email="support@qanooni.com",
    description="Enterprise Azure cost analysis tool with comprehensive reporting",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/CodeVerdict/azure-cost-reporter",
    project_urls={
        "Bug Reports": "https://github.com/CodeVerdict/azure-cost-reporter/issues",
        "Source": "https://github.com/CodeVerdict/azure-cost-reporter",
        "Documentation": "https://github.com/CodeVerdict/azure-cost-reporter#readme",
    },
    py_modules=["azure_cost_analyzer"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "azure-cost-analyzer=azure_cost_analyzer:main",
        ],
    },
    keywords=[
        "azure",
        "cost",
        "analysis",
        "reporting",
        "cloud",
        "monitoring",
        "finance",
        "cli",
        "enterprise",
        "budget",
    ],
    include_package_data=True,
    zip_safe=False,
    platforms=["any"],
) 