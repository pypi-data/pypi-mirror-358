"""
Setup script for wakatimer package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="wakatimer",
    version="2.0.1",
    author="Sukarth Achaya",
    description="Retroactive Time Tracking Data Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sukarth/wakatimer",
    py_modules=["wakatimer"],
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
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wakatimer=wakatimer:main",
        ],
    },
    keywords="time tracking, development tools, productivity, wakatime, simulation",
    project_urls={
        "Bug Reports": "https://github.com/sukarth/wakatimer/issues",
        "Source": "https://github.com/sukarth/wakatimer",
        "Documentation": "https://github.com/sukarth/wakatimer#readme",
    },
)
