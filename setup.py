import os

try:
    from setuptools import setup, find_packages
except ImportError:
    print ("setuptools not installed. run apt-get install python3-setuptools")

from distutils.extension import Extension

def get_long_desc():
    with open("README.md", "r") as readme:
        desc = readme.read()

    return desc


def setup_package():
    setup(
        name='rackops',
        version='0.0.1',
        description='Rack operations',
        long_description=get_long_desc(),
        url='',
        license='MIT',
        packages=find_packages(),
        entry_points = {
            'console_scripts': [
                'rackops=rackops.__main__:main',
            ],
        },
        install_requires=[
            'requests',
            'slimit',
            'bs4',
            ],

    )

if __name__ == '__main__':
    setup_package()
