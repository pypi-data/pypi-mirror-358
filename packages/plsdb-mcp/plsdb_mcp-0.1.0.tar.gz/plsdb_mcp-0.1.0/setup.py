#!/usr/bin/env python3
"""
Setup script for plsdb-mcp package
"""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="plsdb-mcp",
        version="0.1.0",
        description="Model Context Protocol server for interacting with the PLSDB (Plasmid Database) API",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        author="PLSDB MCP Team",
        license="MIT",
        packages=find_packages(),
        install_requires=[
            "mcp>=1.0.0",
            "aiohttp>=3.8.0",
        ],
        python_requires=">=3.8",
        entry_points={
            "console_scripts": [
                "plsdb-mcp=plsdbmcp.main:cli_main",
            ],
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
        ],
    ) 