#!/usr/bin/env python3
"""
Setup script for Azure Resource Graph Client
"""

import os
import re
from setuptools import setup, find_packages


# Read version from __init__.py or version file
def get_version():
    """Extract version from package"""
    try:
        with open(os.path.join("azure_resource_graph", "__init__.py"), "r") as f:
            content = f.read()
            version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
            if version_match:
                return version_match.group(1)
    except FileNotFoundError:
        pass
    return "1.0.0"  # Default version


# Read long description from README
def get_long_description():
    """Read long description from README file"""
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Azure Resource Graph Client for querying Azure resources and checking encryption compliance."


# Read requirements from requirements.txt
def get_requirements():
    """Read requirements from requirements.txt"""
    requirements = []
    try:
        with open("requirements.txt", "r") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    # Extract just the package name and version
                    if line.startswith("azure-identity") or line.startswith("azure-cli-core"):
                        continue  # Skip optional dependencies for core install
                    if any(dev_dep in line for dev_dep in ["pytest", "black", "flake8", "mypy", "sphinx"]):
                        continue  # Skip development dependencies
                    requirements.append(line.split()[0])  # Take first part (removes comments)
        return requirements
    except FileNotFoundError:
        return ["requests>=2.28.0"]


# Core requirements (minimal for basic functionality)
CORE_REQUIREMENTS = [
    "requests>=2.28.0,<3.0.0",
    "python-dotenv>=0.19.0,<2.0.0",
    "pydantic>=2.11.7"
]

# Optional requirements for enhanced functionality
EXTRAS_REQUIRE = {
    "auth": [
        "azure-identity>=1.12.0,<2.0.0",
        "azure-cli-core>=2.40.0,<3.0.0",
    ],
    "dev": [
        "pytest>=7.0.0,<8.0.0",
        "pytest-cov>=4.0.0,<5.0.0",
        "black>=22.0.0,<24.0.0",
        "flake8>=5.0.0,<7.0.0",
        "mypy>=1.0.0,<2.0.0",
    ],
    "docs": [
        "sphinx>=5.0.0,<7.0.0",
        "sphinx-rtd-theme>=1.0.0,<2.0.0",
    ],
}

# All optional dependencies
EXTRAS_REQUIRE["all"] = [
    dep for deps in EXTRAS_REQUIRE.values() for dep in deps
]

setup(
    # Package metadata
    name="azure-resource-graph",
    version=get_version(),
    description="Python client for Azure Resource Graph API with storage encryption analysis",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",

    # Author information
    author="Azure Resource Graph",
    author_email="ken@promptql.io",  # Update with your email
    url="https://github.com/hasura/azure-resource-graph",  # Update with your repo

    # License and classifiers
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],

    # Package discovery
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),

    # Python version requirement
    python_requires=">=3.8",

    # Dependencies
    install_requires=CORE_REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,

    # Package data
    include_package_data=True,
    zip_safe=False,

    # Keywords for PyPI search
    keywords=[
        "azure",
        "resource-graph",
        "cloud",
        "security",
        "encryption",
        "compliance",
        "api-client",
        "kusto",
        "kql"
    ],

    # Project URLs
    project_urls={
        "Documentation": "https://github.com/hasura/azure-resource-graph/blob/main/README.md",
        "Source": "https://github.com/hasura/azure-resource-graph",
        "Tracker": "https://github.com/hasura/azure-resource-graph/issues",
    },

    # Additional metadata
    platforms=["any"],
)
