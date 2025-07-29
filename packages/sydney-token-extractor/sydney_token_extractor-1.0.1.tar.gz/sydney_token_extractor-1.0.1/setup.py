from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sydney-token-extractor",  # Choose a unique name
    version="1.0.1",
    author="Akshay Bhatnagar",
    author_email="akbhatna@microsoft.com",
    description="Setup script for research tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akshaybhatnagar-msft/sydney-token-extractor",  # Your GitHub repo
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "azure-keyvault-secrets>=4.7.0",
        "azure-identity>=1.15.0",
    ],
    entry_points={
        "console_scripts": [
            "sydney-token-extractor=sydney_token_extractor.main:main",
        ],
    },
)