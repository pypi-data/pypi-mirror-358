from setuptools import setup, find_packages
import os

# Read README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="nolink-connector",
    version="1.0.0",
    description="Auto-detecting Socket.IO Terminal Bridge for web platforms",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Sumedh Patil",
    author_email="sumedhpatil99@gmail.com",
    url="https://github.com/Sumedh99/nolink-connector",
    packages=find_packages(),
    install_requires=[
        "python-socketio[client]==5.8.0",
        "aiohttp==3.8.5",
        "psutil==5.9.5",
        "pexpect==4.8.0;platform_system!='Windows'",
        "pywinpty==2.0.12;platform_system=='Windows'",
        "cryptography==41.0.0",
        "asyncpg==0.28.0",
        "python-dotenv==1.0.0",
        "colorama==0.4.6",
        "click==8.1.6"
    ],
    entry_points={
        "console_scripts": [
            "nolink-connector=nolink_connector.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: System Shells",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords="terminal, socketio, web, bridge, automation, shell",
    project_urls={
        "Bug Reports": "https://github.com/Sumedh99/nolink-connector/issues",
        "Source": "https://github.com/Sumedh99/nolink-connector",
        "Documentation": "https://github.com/Sumedh99/nolink-connector#readme",
    },
)
