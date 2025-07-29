import os

from setuptools import find_packages, setup

# Read the README.md for the long description
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pippack",
    version="0.1.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pippack=pippack.main:main',
        ],
    },
    author="Varinder Singh",
    description="A tool to list installed pip packages excluding dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
