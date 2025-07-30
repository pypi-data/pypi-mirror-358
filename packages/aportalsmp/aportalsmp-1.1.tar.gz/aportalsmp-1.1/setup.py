from setuptools import setup, find_packages
import pathlib

cwd = pathlib.Path(__file__).parent
long_description = (cwd / "README.md").read_text()

setup(
    name="aportalsmp",
    version="1.1",
    author="bleach",
    author_email="year0001@internet.ru",
    description="An Asynchronous Python Library for interacting with Portals Marketplace API",
    url="https://github.com/bleach-hub/aportalsmp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "kurigram>=2.2.6",
        "curl_cffi>=0.10.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
