from setuptools import setup, find_packages

setup(
    name="mapconfig",
    version="1.0.0",
    description="A simple Python library for creating interactive maps with markers, circles, and custom icons",
    author="cyrus-spc-tech",
    author_email="tanishgupta12389@gmail.com",
    packages=find_packages(),
    install_requires=[
        "folium>=0.19.0",
        "requests>=2.25.0"
    ],
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
)