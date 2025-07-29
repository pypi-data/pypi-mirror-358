from setuptools import setup
from mypyc.build import mypycify

# All static metadata is now defined in pyproject.toml
# This file is only for the dynamic mypyc compilation.
setup(
    ext_modules=mypycify([
        'pyresult/result.py',
    ]),
)
