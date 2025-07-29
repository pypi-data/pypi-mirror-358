from setuptools import find_packages, setup

setup(
    name="pippack",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pippack=pippack.main:main',
        ],
    },
    author="VSMK",
    description="A tool to list installed pip packages excluding dependencies",
    long_description="A command-line tool that shows the list of installed pip packages excluding their dependencies",
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
