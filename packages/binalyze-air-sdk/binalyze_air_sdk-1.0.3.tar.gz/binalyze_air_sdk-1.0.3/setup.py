from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="binalyze-air-sdk",
    version="1.0.3",
    author="Binalyze",
    author_email="support@binalyze.com",
    description="Complete Python SDK for Binalyze AIR API - 100% API Coverage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/binalyze/air-python-sdk",
    packages=find_packages(exclude=["tests_api", "tests_api.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.1",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "python-dateutil>=2.8.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "isort",
            "mypy",
            "flake8",
        ],
        "testing": [
            "pytest>=6.0",
            "pytest-cov",
            "pytest-mock",
        ],
    },
    keywords="binalyze air forensics security api sdk digital-forensics incident-response",
    project_urls={
        "Bug Reports": "https://github.com/binalyze/air-python-sdk/issues",
        "Source": "https://github.com/binalyze/air-python-sdk",
        "Documentation": "https://github.com/binalyze/air-python-sdk/blob/main/README.md",
    },
)
