"""Setup script for RootzEngine."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
def read_requirements(filename):
    req_path = Path(__file__).parent / "docker" / "requirements" / filename
    if req_path.exists():
        return req_path.read_text().strip().split('\n')
    return []

setup(
    name="rootzengine",
    version="0.1.0",
    description="AI-Powered Reggae Analysis & MIDI Generation Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sonic Codex Team",
    author_email="dev@sonic-codex.com",
    url="https://github.com/sonic-codex/rootzengine",
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    python_requires=">=3.8",
    
    install_requires=read_requirements("base.txt"),
    
    extras_require={
        "dev": read_requirements("dev.txt"),
        "prod": read_requirements("prod.txt"),
    },
    
    entry_points={
        "console_scripts": [
            "rootzengine=rootzengine.scripts.cli:app",
        ],
    },
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    
    keywords="reggae, music, analysis, midi, ai, audio, pattern-recognition",
    
    project_urls={
        "Bug Reports": "https://github.com/sonic-codex/rootzengine/issues",
        "Source": "https://github.com/sonic-codex/rootzengine",
        "Documentation": "https://github.com/sonic-codex/rootzengine/wiki",
    },
    
    include_package_data=True,
    zip_safe=False,
)