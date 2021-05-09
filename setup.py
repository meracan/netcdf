import setuptools
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="netcdf",
    version="0.0.1",
    author="Julien Cousineau",
    author_email="Julien.Cousineau@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meracan/netcdf",
    packages=find_packages(),
    install_requires=['numpy','netcdf4'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)