from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="distributed-logger",
    version="0.1.13",
    author="Arjun Navya",
    author_email="arjun.dahal@navyaadvisors.com",
    description="A lightweight logging system with Kafka support for auditing and debugging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arjun-navya/distributed-logger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Logging",
    ],
    python_requires=">=3.9",
    install_requires=[
        "kafka-python>=2.2.12",
        "python-json-logger>=3.3.0",
        "asgiref>=3.4.1,<3.8.0",
        "Django>=4.0.0,<4.1.0",
        "sqlparse>=0.2.2,<0.5.0",
        "typing_extensions>=4.14.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
) 
