from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Veins',
      version=version,
      description="Simulations of Traffic System Based on the Theory of Cellular Automaton",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='EmdeBoas',
      author_email='emdeboasvan@gmail.com',
      url='https://github.com/xiongbeer/Veins',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          pandas,
          matplotlib,
          numpy
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
