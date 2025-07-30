#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="postgres-mcp-server",
    version="1.0.0",
    author="MCP Community",
    author_email="community@mcp.dev",
    description="A Model Context Protocol server for PostgreSQL databases with SSL support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mcp-community/postgres-mcp-server",
    py_modules=["postgres_mcp_server"],
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "psycopg2-binary>=2.9.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "postgres-mcp-server=postgres_mcp_server:main",
            "postgres-mcp=postgres_mcp_server:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/mcp-community/postgres-mcp-server/issues",
        "Source": "https://github.com/mcp-community/postgres-mcp-server",
        "Documentation": "https://github.com/mcp-community/postgres-mcp-server/blob/main/README.md",
        "Homepage": "https://modelcontextprotocol.io",
    },
    keywords=["mcp", "postgresql", "database", "ai", "llm", "model-context-protocol"],
)
