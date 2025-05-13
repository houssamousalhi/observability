from setuptools import find_packages, setup

setup(
    name="source_alarm_demo",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.26.79",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.5",
            "pytest-mock>=3.10.0",
        ],
    },
)
