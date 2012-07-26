import twisterman
from setuptools import setup, find_packages

setup(
    name = 'twisterman',
    version = twisterman.__version__,
    packages = find_packages(),
    scripts = ('scripts/twisterman',),
    install_requires = ['Twisted', 'PyYAML'],
)
