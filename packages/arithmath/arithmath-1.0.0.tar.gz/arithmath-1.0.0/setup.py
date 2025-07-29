from setuptools import setup, find_packages
import os

version_file =  os.path.join("arithmath", "__init__.py")

def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

def get_version() -> str:
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
            
    raise RuntimeError("Unable to find version string!")

def get_author() -> str:
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__author__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    
    raise RuntimeError("Unable to find author string!")

def get_author_email() -> str:
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__email__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    
    raise RuntimeError("Unable to find E-mail string!")


setup(
    name="arithmath",
    version=get_version(),
    author=get_author(),
    author_email=get_author_email(),
    description="A mathematical utils package",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/harrshjain/arithmath",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[],
    include_package_data=True,
    zip_safe=False
)