#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT设备交互库安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aioeway",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="一个基于异步编程的MQTT设备通信库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aioeway",
    packages=find_packages(),
    py_modules=["device_mqtt_client"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware",
        "Topic :: Communications",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        'aiomqtt>=2.0.0',
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "device-mqtt-example=example:main",
        ],
    },
    keywords="mqtt, iot, device, communication, monitoring",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/device-mqtt-client/issues",
        "Source": "https://github.com/yourusername/device-mqtt-client",
        "Documentation": "https://github.com/yourusername/device-mqtt-client/blob/main/README.md",
    },
)