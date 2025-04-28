from setuptools import find_packages, setup

setup(
    name="source_alarm_forwarder",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "pytest",
    ],
)
