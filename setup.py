import setuptools
from setuptools import find_packages

with open("pc_client/requirements.txt") as req_f:
    requirements = req_f.read().splitlines()

setuptools.setup(
    name="PersistentConnectionServer",
    version="1.0",
    packages=find_packages(exclude=["example_protocol", "performance_tests"]),
    requires=["wheel"],
    install_requires=requirements
)
