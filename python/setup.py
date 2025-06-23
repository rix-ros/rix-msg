from setuptools import setup, find_packages

setup(
    name='rixmsg',
    version='0.1.0',
    description='RIX message serialization library',
    author='Broderick Riopelle',
    author_email='broderio@umich.edu',
    packages=find_packages(),
    python_requires='>=3.6',
)