"""
Setup script for Box Packer application.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="box-packer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Optimal pallet arrangement calculator for rectangular boxes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/box-packer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "box-packer=main_new:main",
        ],
    },
    keywords="pallet, boxes, optimization, logistics, packaging, arrangement, visualization",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/box-packer/issues",
        "Source": "https://github.com/yourusername/box-packer",
        "Documentation": "https://github.com/yourusername/box-packer#readme",
    },
)
