from setuptools import setup, find_packages

setup(
    name="greenfootprint",
    version="0.1.0",
    description="Estimate energy and carbon footprint of Python scripts",
    author="Thuverakan Tharumakulasooriyan",
    author_email="thuverakantharma@gmail.com",
    packages=find_packages(),
    install_requires=["psutil"],
    entry_points={
        "console_scripts": [
            "green-py = greenpy.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
