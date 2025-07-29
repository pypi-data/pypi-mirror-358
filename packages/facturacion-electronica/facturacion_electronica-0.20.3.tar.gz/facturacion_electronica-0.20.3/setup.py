# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

pkg_vars = {}
with open('facturacion_electronica/_version.py') as fp:
    exec(fp.read(), pkg_vars)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
        name='facturacion_electronica',
        version=pkg_vars['__version__'],
        packages=find_packages(),
        package_data={'facturacion_electronica': ['xsd/*.xsd']},
        install_requires=[
            'lxml',
            'cryptography==41.0.7',
            'pyOpenSSL==23.2.0',
            'certifi',
            'pytz',
            'pdf417gen>=0.6.0',
            'zeep>=3.4.0',
            'urllib3',
            'requests>=2.24.0',
        ],
        author='Daniel Santibáñez Polanco',
        author_email='dansanti@gmail.com',
        url='https://gitlab.com/dansanti/facturacion_electronica',
        license='GPLV3+',
        long_description=long_description,
        long_description_content_type='text/markdown',
        classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Programming Language :: Python :: 3.6',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Environment :: Console',
        ]
       )
