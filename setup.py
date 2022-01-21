import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname: str) -> str:
    """ Utility function to read the README file used for the long_description.

    Args:
        fname (str): File name of the README file

    Returns:
        str: Content of the README file.
    """
    return open(os.path.join(os.path.dirname(__file__), fname),
                encoding='utf8').read()


setup(name="quality_assessor",
      version="1.0b1",
      author="Veit Grosse",
      author_email="veit.grosse@gmail.com",
      description=(""),
      license="BSD",
      keywords="example documentation tutorial",
      url="http://packages.python.org/an_example_pypi_project",
      packages=['quality_assessor', 'tests'],
      long_description=read('README.md'),
      classifiers=[
          "Development Status :: 4 - Beta",
          "Topic :: Utilities",
          "License :: OSI Approved :: BSD License",
      ],
      install_requires=['matplotlib', 'numpy', 'pandas', 'fpdf2', 'scipy'])
