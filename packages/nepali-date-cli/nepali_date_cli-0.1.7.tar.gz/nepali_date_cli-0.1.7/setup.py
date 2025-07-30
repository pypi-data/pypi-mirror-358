from setuptools import setup, find_packages

setup(
    name="nepali-date-cli",
    version="0.1.7",
    packages=find_packages(),
    install_requires=[
        "nepali-datetime",
    ],
    entry_points={
        "console_scripts": [
            "miti=nepali_date_cli.cli:main",
            "nepdate=nepali_date_cli.cli:deprecated_main",
        ],
    },
    author="Nishant Thapa",
    author_email="itsnishantu@gmail.com",
    description="A command-line tool to display Nepali date in your terminal.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/itznishantthapa/nepdate",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 