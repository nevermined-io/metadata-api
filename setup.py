#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

    install_requirements = [
    'coloredlogs==10.0',
    'Flask==1.1.2',
    'Flask-Cors==3.0.9',
    'flask-swagger==0.2.14',
    'flask-swagger-ui==3.25.0',
    'Jinja2>=2.10.1',
    'requests>=2.23.0',
    'gunicorn==19.9.0',
    'nevermined-metadata-driver-interface>=0.1.3',
    'nevermined-metadata-driver-mongodb>=0.1.0',
    'nevermined-metadata-driver-elasticsearch>=0.1.0',
    'PyYAML==5.1',
    'pytz==2018.5'
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
    version='0.2.1',
    zip_safe=False,
)
