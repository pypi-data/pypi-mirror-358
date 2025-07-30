from setuptools import setup, find_packages

setup(
    name="aipmodel",  # The name of the package that will be used to install it via pip
    version="0.2.1",  # Version number of the package
    description="A simple SDK for managing ML models",  # Short description of your package
    author="AIP MLOPS Team",  # Author's name
    author_email="mohmmadweb@gmail.com",  # Author's email address
    url="https://github.com/AIP-MLOPS/model-registry",  # URL to the GitHub repository
    packages=find_packages(),  # Automatically find packages to include
    install_requires=[],  # List dependencies here if your package has any
    python_requires=">=3.6",  # Python version requirement
)
