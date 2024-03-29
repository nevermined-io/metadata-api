#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

    install_requirements = [
    'coloredlogs==15.0.1',
    'Flask==2.1.1',
    'Flask-Cors==3.0.10',
    'flask-swagger==0.2.14',
    'flask-swagger-ui==3.36.0',
    'Jinja2>=2.10.1',
    'requests>=2.23.0',
    'gunicorn==20.1.0',
    'nevermined-metadata-driver-interface>=0.2.0',
    'nevermined-metadata-driver-mongodb>=0.1.0',
    'nevermined-metadata-driver-elasticsearch>=0.1.6',
    'nevermined-metadata-driver-arweave>=0.1.4',
    'PyYAML==5.4.1',
    'pytz==2021.1',
    'uwsgidecorators==1.1.0',
    'uWSGI==2.0.19.1'
]

setup_requirements = ['pytest-runner', ]

dev_requirements = [
    'bumpversion',
    'pkginfo',
    'twine',
    # not virtualenv: devs should already have it before pip-installing
    'watchdog',
]

test_requirements = [
    'coverage',
    'mccabe',
    'pylint',
    'pytest',
]

setup(
    author="nevermined-io",
    author_email='root@nevermined.io',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Nevermined metadata.",
    extras_require={
        'test': test_requirements,
        'dev': dev_requirements + test_requirements,
    },
    include_package_data=True,
    install_requires=install_requirements,
    keywords='nevermined-metadata',
    license="Apache Software License 2.0",
    long_description=readme,
    long_description_content_type="text/markdown",
    name='nevermined-metadata',
    packages=find_packages(include=['nevermined_metadata', 'nevermined_metadata.app']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/nevermined-io/metadata-api',
    version='0.6.1',
    zip_safe=False,
)
