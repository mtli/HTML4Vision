"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from setuptools import setup
# codes.open is for support of python 2.x
from codecs import open
from os import path

import re

here = path.abspath(path.dirname(__file__))
re_ver = re.compile(r"__version__\s+=\s+'(.*)'")
with open(path.join(here, 'html4vision', '__init__.py'), encoding='utf-8') as f:
    version = re_ver.search(f.read()).group(1)

setup(
    name='HTML4Vision',
    version=version,
    description='A simple HTML visualization tool for computer vision research',
    long_description='See project page: https://github.com/mtli/HTML4Vision',
    url='https://github.com/mtli/HTML4Vision',
    author='Mengtian (Martin) Li',
    author_email='martinli.work@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='research computer vision visualization',
    packages=['html4vision'],
    install_requires=[
        'Flask',
        'dominate',
    ],
    include_package_data = True,
)
