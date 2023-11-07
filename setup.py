from setuptools import setup, find_packages

setup(
    name='quaderno_sdk',
    version='0.0.5',
    install_requires=[
        'requests==2.30.0',
    ],
    packages=find_packages(),
)