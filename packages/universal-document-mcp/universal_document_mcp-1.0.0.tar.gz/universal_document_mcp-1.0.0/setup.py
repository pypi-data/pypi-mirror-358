#!/usr/bin/env python3
"""
Setup script for Universal Document Converter MCP Server
Provides system-wide installation for Python-based MCP server
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = this_directory / "requirements-mcp.txt"
    if requirements_path.exists():
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        "mcp>=1.0.0",
        "playwright>=1.40.0",
        "markdown>=3.5.0",
        "requests>=2.31.0",
        "asyncio-mqtt>=0.13.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0"
    ]

# Get version from package
def get_version():
    version_file = this_directory / "universal_document_mcp" / "__version__.py"
    if version_file.exists():
        version_dict = {}
        with open(version_file, 'r') as f:
            exec(f.read(), version_dict)
            return version_dict.get('__version__', "1.0.0")
    return "1.0.0"

setup(
    name="universal-document-mcp",
    version=get_version(),
    author="AUGMENT AI Assistant",
    author_email="support@augment.ai",
    description="Universal Document Converter MCP Server - AI-powered markdown to PDF conversion with Mermaid support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/augment-ai/universal-document-mcp",
    project_urls={
        "Bug Reports": "https://github.com/augment-ai/universal-document-mcp/issues",
        "Source": "https://github.com/augment-ai/universal-document-mcp",
        "Documentation": "https://github.com/augment-ai/universal-document-mcp#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Utilities",
        "Environment :: Console",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "ai": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
        ],
        "full": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "universal-document-mcp=universal_document_mcp.server:main",
            "udmcp=universal_document_mcp.server:main",
            "universal-doc-mcp=universal_document_mcp.server:main",
            "mcp-document-converter=universal_document_mcp.server:main",
        ],
        "mcp.servers": [
            "universal-document-converter=universal_document_mcp.server:create_server",
        ]
    },
    package_data={
        "universal_document_mcp": [
            "templates/*.html",
            "templates/*.css",
            "config/*.json",
            "config/*.yaml",
            "scripts/*.py",
            "scripts/*.js",
        ]
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "mcp", "server", "document", "converter", "markdown", "pdf", 
        "mermaid", "diagrams", "ai", "claude", "cline", "vscode"
    ],
    platforms=["any"],
    license="MIT",
    # Post-install script to set up Playwright
    cmdclass={},
)

# Post-installation setup
def post_install():
    """Run post-installation setup"""
    try:
        import subprocess
        print("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      check=True, capture_output=True)
        print("✅ Playwright browsers installed successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not install Playwright browsers: {e}")
        print("Please run 'python -m playwright install chromium' manually")

if __name__ == "__main__":
    setup()
    if "install" in sys.argv:
        post_install()
