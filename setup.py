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
