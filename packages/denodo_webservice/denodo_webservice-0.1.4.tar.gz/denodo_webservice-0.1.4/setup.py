# https://stackoverflow.com/questions/74968585/using-environment-variables-in-pyproject-toml-for-versioning
import os

import my_package
from setuptools import setup

dev_version = os.environ.get("DEV_VERSION")

setup(version=dev_version if dev_version else f"{my_package.__version__}")
