"""
Setup script for Opus One Audio Visualizer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="opus-one",
    version="1.0.0",
    author="voidfnc",
    author_email="",
    description="A stunning audio visualizer with real-time spectrum analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/voidfnc/warp-opus",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.11",
    install_requires=[
        "PyQt6>=6.5.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pyaudio>=0.2.11",
        "pydub>=0.25.1",
    ],
    entry_points={
        "console_scripts": [
            "opus-one=main:main",
        ],
    },
)
