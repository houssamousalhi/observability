from setuptools import setup, find_packages

setup(
    name="source-grafana-cw-datasource-key-rotator",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.26.79",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.5",
            "pytest-mock>=3.10.0",
        ],
    },
)
