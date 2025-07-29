from setuptools import setup, find_packages
import os

# Lire les scripts bash
def read_script(filename):
    with open(os.path.join("fdock_cli", "scripts", filename), "r") as f:
        return f.read()

setup(
    name="fdock-cli",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "fdock_cli": ["scripts/*.sh"],
    },
    entry_points={
        "console_scripts": [
            "fdock=fdock_cli.cli:main",
        ],
    },
    install_requires=[],
    author="Your Name",
    author_email="your.email@example.com",
    description="Un CLI pour initialiser des projets Python avec des scripts bash utiles",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fdock-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
