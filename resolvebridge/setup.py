""" Setup.py """

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    _license = f.read()

setup(
    name='Resolve-Bridge',
    version='0.1.0',
    description='Scripts for DaVinci Resolve API',
    long_description=readme,
    author='Caleb Trevatt',
    author_email='in03@users.noreply.github.com',
    url='https://github.com/kennethreitz/samplemod',
    license=_license,
    packages=find_packages(exclude=('tests', 'docs'))
)
