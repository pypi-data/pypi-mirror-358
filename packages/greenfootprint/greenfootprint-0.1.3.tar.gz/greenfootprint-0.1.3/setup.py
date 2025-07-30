from setuptools import setup, find_packages
from pathlib import Path

# Load README.md content for PyPI description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="greenfootprint",  # ✅ Unique name
    version="0.1.3",
    description="Estimate energy and carbon footprint of Python scripts",
    long_description=long_description,  # ✅ For PyPI description
    long_description_content_type="text/markdown",  # ✅ It's markdown!
    author="Thuverakan Tharumakulasooriyan",
    author_email="thuverakantharma@gmail.com",
    url="https://github.com/thuve-codes/greenfootprint",  # optional but recommended
    packages=find_packages(),
    install_requires=["psutil"],
    entry_points={
        "console_scripts": [
            "greenfootprint = greenfootprint.cli:main",  # CLI command name
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
