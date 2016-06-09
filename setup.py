#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name="Chandere",
      license="GPLv3",
      version="0.1.0dev1",
      author="Jakob Tsar-Fox",
      author_email="jakob@memeware.net",
      maintainer="Jakob Tsar-Fox",
      maintainer_email="jakob@memeware.net",
      url="http://tsar-fox.com/projects/chanworks",
      description="Web scraper to download posts and images from various imageboards.",
      long_description="Generalized scraper for Futaba-styled imageboards, such as 4chan. Capabilities range from downloading images to archiving entire boards.",
      download_url="",
      packages=["chandere"],
      include_package_data=True,
      install_requires=[],
      extras_require={},
      entry_points={"console_scripts": ["chandere = chandere.cli:main"]}
     )
