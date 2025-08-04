"""Setup script for RootzEngine."""

from setuptools import setup, find_packages

# Read the contents of requirements-dev.txt for development setup
with open("requirements-dev.txt") as f:
    requirements = [
        line.strip()
        for line in f.readlines()
        if not line.startswith("#") and line.strip() and not line.startswith("-r")
    ]

# Read the README.md for the long description
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rootzengine",
    version="0.1.0",
    description="AI-Powered Reggae Metadata + Groove Generation Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RootzEngine Team",
    author_email="info@rootzengine.com",
    url="https://github.com/your-username/rootzengine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rootzengine=rootzengine.cli:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
