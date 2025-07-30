
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="discordmusiclib",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A custom YouTube audio downloader for Discord bots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/discordmusiclib",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "discord.py>=2.0.0",
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8"],
    },
    keywords="discord, music, youtube, audio, bot",
)
