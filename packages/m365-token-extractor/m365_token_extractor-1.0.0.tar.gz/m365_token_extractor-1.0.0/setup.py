from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="m365-token-extractor",  # Choose a unique name
    version="1.0.0",
    author="Akshay Bhatnagar",
    author_email="akbhatna@microsoft.com",
    description="Setup script for research tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akshaybhatnagar-msft/m365-token-extractor",  # Your GitHub repo
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
            "m365-token-extractor=token_extractor.main:main",
        ],
    },
)