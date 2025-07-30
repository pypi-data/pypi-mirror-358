#!/usr/bin/env python

from distutils.core import setup

PACKAGE_NAME = "tnggui"
#
# this is the source version
#
(major, minor, patch) = (2, 0, 0)
version = "%s.%s.%s" % (major, minor, patch)

setup(name=PACKAGE_NAME,
      version=version,
      author="Thorsten Kracht",
      author_email="fs-ec@desy.de",
      url="https://gitlab.desy.de/fs-ec/TngGui",
      scripts=['tngGui/bin/TngGui.py'],
      packages=['tngGui', 'tngGui/lib'])
