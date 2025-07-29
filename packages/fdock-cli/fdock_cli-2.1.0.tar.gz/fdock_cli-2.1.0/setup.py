from setuptools import setup, find_packages

setup(
    name="fdock_cli",
    version="2.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'fdock=fdock_cli.cli:main',
        ],
    },
    package_data={
        'fdock_cli': ['scripts/*.sh'],
    },
) 