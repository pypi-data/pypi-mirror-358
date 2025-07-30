import os
import json
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'version.json')) as f:
    version = json.loads(f.read())


setup(
    name='fxpyD365api',
    description='Wrapper classes for working with Dynamics 365 web API entities.',
    version=version,
    author='Flexit developers',
    author_email='westma@flexit.no',
    packages=find_packages(exclude=("dev", "dev.*")),
    license='BSD',
    url="https://github.com/flexitdev/fxpyD365api",
    install_requires=[
        'requests>=2.20.0',
        'urllib3>=1.26.0,<3.0.0',  # used explicitly via Retry in sync.py
        'msal',
        'aiohttp',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)