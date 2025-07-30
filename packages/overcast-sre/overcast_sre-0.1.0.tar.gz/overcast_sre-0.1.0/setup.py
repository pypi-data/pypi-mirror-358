#!/usr/bin/env python3
"""Setup script for Overcast SDK"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Overcast SDK - AI-powered monitoring and incident management for startups"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return ["flask>=2.0.0", "rich>=10.0.0", "requests>=2.25.0", "openai>=1.0.0"]

setup(
    name="overcast-sre",
    version="0.1.0",
    description="AI-powered monitoring and incident management for startups - 3-line integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Overcast",
    author_email="raghavb5120@gmail.com",
    url="https://github.com/overcast-ai/overcast-sre",
    py_modules=["overcast"],
    packages=find_packages(include=["core", "core.*"]),
    install_requires=read_requirements(),
    python_requires=">=3.8",
    
    # Package data
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "*.md", "*.txt"],
    },
    
    # Entry points for command line tools
    entry_points={
        "console_scripts": [
            "overcast=overcast:main",
            "overcast-cli=cli:main",
        ],
    },
    
    # Classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    
    # Keywords
    keywords="monitoring observability incidents alerting ai analytics dashboard startup sre",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/overcast-ai/overcast-sre/issues",
        "Source": "https://github.com/overcast-ai/overcast-sre", 
        "Documentation": "https://github.com/overcast-ai/overcast-sre#readme",
        "Dashboard": "https://overcast.up.railway.app",
    },
    
    # Additional metadata
    zip_safe=False,
) 