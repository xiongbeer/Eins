#!/usr/bin/python

from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='EinsPy',
      version=version,
      description="Simulations of Traffic System Based on the Theory of Cellular Automaton",
      long_description="""\
      Simulations of Traffic System Based on the Theory of Cellular Automaton
""",
      classifiers=[
            "License :: OSI Approved :: MIT License",
            "Development Status :: 3 - Alpha",
            "Natural Language :: Chinese (Simplified)",
            "Programming Language :: Python :: 2.7",
            "Topic :: Scientific/Engineering :: Mathematics"
      ],
      author='xiongbeer',
      author_email='xiongshaoliu@163.com',
      url='https://github.com/xiongbeer/Eins',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'pandas',
          'matplotlib',
          'numpy',
          'colorama'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
