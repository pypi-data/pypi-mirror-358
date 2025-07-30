"""
ZapSEA Python SDK Setup Configuration
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "ZapSEA Python SDK for policy intelligence and impact analysis"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return ["httpx>=0.24.0", "pydantic>=1.10.0"]

setup(
    name="zapsea",
    version="1.0.0",
    description="Official Python SDK for the ZapSEA Intelligence Engine API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="ZapSEA Team",
    author_email="support@polityflow.com",
    url="https://github.com/Travvy-McPatty/ZapSEA",
    project_urls={
        "Documentation": "https://docs.polityflow.com/sdk/python",
        "Source": "https://github.com/Travvy-McPatty/ZapSEA/tree/main/sdks/python",
        "Tracker": "https://github.com/Travvy-McPatty/ZapSEA/issues",
        "API Reference": "https://api.polityflow.com/docs"
    },
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0"
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.19.0"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Legal Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed"
    ],
    keywords=[
        "policy", "analysis", "intelligence", "government", "regulation",
        "impact", "simulation", "lobbying", "compliance", "api", "sdk"
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "zapsea=zapsea.cli:main",
        ],
    }
)
