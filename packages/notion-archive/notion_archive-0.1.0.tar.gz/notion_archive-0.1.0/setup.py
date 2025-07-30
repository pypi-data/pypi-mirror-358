"""
Setup script for Notion Archive
"""

from setuptools import setup, find_packages
import os

# Read the README file for the long description
def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return ""

# Core dependencies
install_requires = [
    "beautifulsoup4>=4.9.0",
    "chromadb>=0.4.0",
    "langchain>=0.1.0",
    "numpy>=1.20.0",
    "pathlib",
    "sentence-transformers>=2.0.0",
]

# Optional dependencies
extras_require = {
    "openai": ["openai>=1.0.0"],
    "dev": [
        "pytest>=6.0.0",
        "pytest-cov>=2.10.0",
        "black>=21.0.0",
        "flake8>=3.8.0",
        "mypy>=0.800",
    ],
    "all": ["openai>=1.0.0"],
}

setup(
    name="notion-archive",
    version="0.1.0",
    author="Notion Archive Contributors",
    author_email="hello@notion-archive.com",
    description="Simple semantic search for Notion HTML exports using AI embeddings",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/otron-io/notion-archive",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    keywords="notion, search, ai, embeddings, knowledge-base, vector-search, semantic-search",
    project_urls={
        "Bug Reports": "https://github.com/otron-io/notion-archive/issues",
        "Source": "https://github.com/otron-io/notion-archive",
        "Documentation": "https://github.com/otron-io/notion-archive#readme",
    },
)