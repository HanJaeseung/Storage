from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'cytest app',
  ext_modules = cythonize("pysrc/*.py"),
)
