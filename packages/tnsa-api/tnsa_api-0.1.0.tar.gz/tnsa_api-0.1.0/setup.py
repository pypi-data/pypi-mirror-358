from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

with open(here / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tnsa-api",
    version="0.1.0",
    description="Python SDK for TNSA AI API (model inference and management)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TNSA AI Team",
    url="https://github.com/tnsaai/platform.tnsaai.com",  # Update if you have a public repo
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
)