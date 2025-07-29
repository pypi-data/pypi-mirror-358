from setuptools import setup, find_packages

setup(
    name="apal-client",
    version="0.1.0",
    packages=["apal_client"],
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.7.0",
        "python-dotenv>=1.0.0"
    ],
    author="Ming-Chang Chiu",
    author_email="contact@apal-ai.com",
    description="Python client library for APAL secure P2P communication platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/charismaticchiu/apal-client",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 