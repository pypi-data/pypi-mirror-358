# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wrd",
    version="1.0.0",
    author="Claude Code User",
    author_email="user@example.com",
    description="WRD (Word) - Narzędzie workflow dla Claude Code na Fedorze",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/wrd",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: Apache License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=12.0.0",
        "pydantic>=1.9.0",
        "python-dotenv>=0.19.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "data": [
            "pandas>=1.5.0",
            "numpy>=1.24.0",
            "matplotlib>=3.6.0",
        ],
        "web": [
            "fastapi>=0.95.0",
            "uvicorn>=0.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wrd=wrd.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "wrd": ["templates/*", "configs/*"],
    },
)
