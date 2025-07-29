#!/usr/bin/env python

from setuptools import setup, find_packages

long_desc = open("README.rst").read()
version = open("version").read().strip()

setup(name='PyWebDAV3-GNUHealth',
      version=version,
      description='WebDAV library for Python3 - GNU Health port',
      author='GNU Solidario',
      author_email='health@gnusolidario.org',
      download_url='https://ftp.gnu.org/gnu/health/',
      maintainer='GNU Health team',
      maintainer_email='info@gnuhealth.org',
      url='https://www.gnuhealth.org',
      platforms=['Unix'],
      license='GPL v3',
      long_description=long_desc,
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        ],
      keywords=['webdav',
                'GNUHealth',
                'server',
                'dav',
                'standalone',
                'library',
                'gpl',
                'http',
                'rfc2518',
                'rfc 2518'
                ],
      packages=find_packages(),
      zip_safe=False,
      entry_points={
        'console_scripts': ['davserver = pywebdav.server.server:run']
        },
      )
