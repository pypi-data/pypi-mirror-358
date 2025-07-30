
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="discord-music-streamer",
    version="0.1.1",
    author="Your Name",
    author_email="you@example.com",
    description="A Python library for streaming music in Discord voice channels with YouTube support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/discord-music-streamer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "discord.py[voice]>=2.0.0",
        "aiohttp>=3.8.0",
        "PyNaCl>=1.5.0",
    ],
    keywords="discord music bot youtube streaming voice",
)
