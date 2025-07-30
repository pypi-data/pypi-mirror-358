#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setup(
  name="pdf-unlocker",
  version="1.3",
  packages=find_packages(),
  entry_points={
    'console_scripts': [
      'pdf-unlocker = pdf_unlocker.__main__:main',
    ],
  },
  url="https://github.com/jfhack/pdf-unlocker",
  install_requires=[
    'pikepdf'
  ],
  long_description=long_description,
  long_description_content_type="text/markdown"
)
