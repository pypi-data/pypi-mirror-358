from setuptools import setup, find_packages

setup(
    name='kotlinwrapper1',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={'kotlinwrapper1': ['temp.txt']},
    description='A test package that includes temp.txt',
    author='Your Name',
)
