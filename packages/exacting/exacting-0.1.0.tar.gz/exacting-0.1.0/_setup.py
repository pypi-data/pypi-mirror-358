from setuptools import setup
from Cython.Build import cythonize

setup(
    name="python/exacting/",
    ext_modules=cythonize(
        [
            "python/exacting/etypes.py",
            "python/exacting/dc.py",
            "python/exacting/core.py",
        ]
    ),
    package_dir={"": "python"},
)
