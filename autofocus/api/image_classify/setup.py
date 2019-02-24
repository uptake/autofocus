from setuptools import setup, find_packages
import sys

assert sys.version[0] == '3'  # this would only run on 3

VERSION = "0.0.2"

install_requires = ['tensorflow==1.9.0',
                    'numpy']

setup(name='image_classify',
      version=VERSION,
      description='Package for doing image classification with tensorflow',
      author='Uptake Data Science',
      author_email='daniel.acheson@uptake.com',
      license='Double Super Secret License',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires
      )