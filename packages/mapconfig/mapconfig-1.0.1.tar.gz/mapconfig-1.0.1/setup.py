from setuptools import setup, find_packages

setup(
    name="mapconfig",
    version="1.0.1",
    description="A simple Python library for creating interactive maps with markers, circles, and custom icons",
    author="cyrus-spc-tech",
    author_email="tanishgupta12389@gmail.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
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