# NOTE:
# This file is an exact replica of the setup.py stored at the root of the
# kubails repo. It _must_ be kept perfectly in sync. The reason being that
# this setup.py is used by the kubails-builder to install kubails inside itself
# during the Docker image build.
# This is done because the kubails code is not yet public, so it can't
# just be `pip install`d from pypi.

from setuptools import setup, find_packages

setup(
    name="Kubails",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click>=7.0",
        "typing>=3.6.4",
        "cookiecutter>=1.6.0",
        "pyyaml>=4.2b4",
        "python-dotenv>=0.10.1",
        "requests>=2.21.0"
    ],
    entry_points={
        "console_scripts": [
            "kubails = kubails.main:cli"
        ]
    }
)
