#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name="Chandere",
      license="GPLv3",
      version="0.1.1dev1",
      author="Jakob Tsar-Fox",
      author_email="jakob@memeware.net",
      maintainer="Jakob Tsar-Fox",
      maintainer_email="jakob@memeware.net",
      url="http://tsar-fox.com/projects/chandere",
      description="Web scraper to download posts and images from various imageboards.",
      long_description="Generalized scraper for Futaba-styled imageboards, such as 4chan. Capabilities range from downloading images to archiving entire boards.",
      download_url="",
      packages=["chandere"],
      include_package_data=True,
      install_requires=[],
      extras_require={},
      entry_points={"console_scripts": ["chandere = chandere.cli:main"]},
      classifiers=[
          'Development Status :: 1 - Planning',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Text Processing',
          'Topic :: Utilities'
      ],
     )
