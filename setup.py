# -*- encoding: utf-8 -*-
from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

setup(
    name='pyfuppes',
    version='2020.6.8a',
    license='MIT',
    description='MrFuppes collection of tools in Python',
    author='Florian Obersteiner',
    author_email='f.obersteiner@kit.edu',
    url='https://github.com/MrFuppes/pyfuppes',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
)
