#!/usr/bin/env python3
"""Setup script for Global Scripts"""

from pathlib import Path
import subprocess
import sys

# --- Standard setuptools build section ---
try:
    from setuptools import setup
    setup(
        name="repository-builder",
        version="1.0.0",
        description="A comprehensive collection of Python scripts and tools for enhanced productivity.",
        author="Gina R. Rodriguez",
        author_email="DCV5793@tn.gov",
        readme="README.md",
        license_files=("LICENSE",),
        python_requires=">=3.7",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent"
        ],
        url="https://github.com/gwanczuk/Repository-Builder",
        project_urls={
            "Homepage": "https://github.com/gwanczuk/Repository-Builder",
            "Bug Tracker": "https://github.com/gwanczuk/Repository-Builder/issues"
        },
        packages=[],  # You can update this if you have importable packages
        install_requires=[],
    )
except ImportError:
    pass  # Allows running as a script for environment setup

# --- Custom environment setup script ---
def setup_environment():
    """Set up the Global Scripts environment."""
    print("🔧 Global Scripts Setup")
    print("=" * 30)

    current_dir = Path.cwd()
    print(f"📁 Setting up in: {current_dir}")

    # Create directories
    directories = ["src", "scripts", "Documentation_DOCX", "templates", "backups"]
    for dir_name in directories:
        dir_path = current_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"📁 Created: {dir_name}/")

    # Install dependencies
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
        print("✅ python-docx installed")
    except subprocess.CalledProcessError:
        print("⚠️ Failed to install python-docx. Install manually: pip install python-docx")

    print("\n✅ Setup complete!")
    print("🚀 Run: python global_manager.py --help")

if __name__ == "__main__":
    setup_environment()
