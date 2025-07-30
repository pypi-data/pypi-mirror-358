from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vocalysis",
    version="0.2.1",
    author="Łukasz Stolarski",
    description="A Python package for voice analysis using Praat and Parselmouth.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Stolarski-Lukasz/vocalysis",
    packages=find_packages(),
    install_requires=[
        "praat-parselmouth>=0.4.4",
        "numpy>=1.26.0",
    ],
    license="GPL-3.0-or-later",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires='>=3.7',
)

