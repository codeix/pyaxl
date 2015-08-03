from setuptools import setup, find_packages
import os

version = '1.0'

long_description = (
    open('README.rst').read()
    + '\n\n\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(name='pyaxl',
      version=version,
      description="pyaxl is a python library accessing the Cisco Callmanger over the AXL interface",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Programming Language :: Python :: 3 :: Only',
          'Natural Language :: English',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Development Status :: 4 - Beta'
          
      ],
      keywords='bielbienne cisco callmanger axl soap',
      author='Samuel Riolo',
      author_email='samuel.riolo@biel-bienne.ch',
      url='https://github.com/bielbienne/pyaxl',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'suds-jurko'
      ],
      tests_require=[
          'suds-jurko',
      ],
      test_suite='pyaxl.testing.test_suite',
      entry_points={
          'console_scripts': ['pyaxl_import_wsdl = pyaxl.axlhandler:import_wsdl'],
      })
