from setuptools import find_packages
from setuptools import setup

with open("PYPI_README.md") as f:
    long_description = f.read()

setup(
    name="velosaurus_calc",
    version="1.0.10",
    description="Most awesome math package ever.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Oliver Zott",
    author_email="zott_oliver@web.de",
    url="https://github.com/OliverZott/python-devops-example",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Add any dependencies your project requires
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
