import setuptools
from setuptools import find_packages

setuptools.setup(
    name="PersistentConnectionServer",
    version="1.0",
    packages=find_packages(exclude=["example_protocol", "performance_tests"]),
)
