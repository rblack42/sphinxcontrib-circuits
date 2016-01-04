# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


requires = ['Sphinx>=0.6']

setup(
    name='sphinxcontrib-circuits',
    version='1.5.4',
    url='https://github.com/rblack42/sphinxcontrib-circuits',
    license='BSD',
    author='Roie R. Black',
    author_email='rblack@austincc.edu',
    description='Sphinx "M4 Circuits" extension',
    long_description=open("README.rst").read(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)

