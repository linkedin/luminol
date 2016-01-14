#! /usr/bin/python

from setuptools import setup, find_packages

with open('VERSION') as f:
      luminol_version = f.read().strip()

with open('requirements.txt') as f:
      required = f.read().splitlines()

setup(name="luminol",
      description='luminol is an anomaly detection and correlation library for timeseries data.',
      url='https://github.com/linkedin/luminol',
      author='Naarad Developers',
      author_email='naarad-dev@googlegroups.com',
      version=luminol_version,
      packages=['luminol', 'luminol.algorithms', 'luminol.modules', 'luminol.algorithms.anomaly_detector_algorithms',
                'luminol.algorithms.correlator_algorithms'],
      package_dir={'': 'src'},
      install_requires=required,
      license='Apache 2.0',
      )
