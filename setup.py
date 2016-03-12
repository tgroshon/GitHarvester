import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from githarvester import __version__
from setuptools import setup, find_packages

setup(
    name = 'githarvester',
    packages = find_packages(),
    version = __version__,
    description = 'This tool is used for harvesting information from GitHub.',
    author = 'Metacortex',
    author_email = 'metacortex@someplace.com', # update this
    url = 'https://github.com/metac0rtex/GitHarvester',
    download_url = 'https://github.com/metac0rtex/GitHarvester/tarball/' + __version__, # just git tag your stuff
    keywords = ['security', 'osint', 'githarvester'],
    classifiers = [],
    entry_points={
        # Create executable script on Mac and Windows
        'console_scripts': [
            'githarvest = githarvester.core:main'
        ]
    },
    install_requires=[
        'argparse',
        'beautifulsoup4',
        'pycurl'
    ]
)
