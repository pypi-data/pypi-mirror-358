# setup.py
from setuptools import setup, find_packages
import os

# dynamically find the package name and version file
base_dir = os.path.abspath(os.path.dirname(__file__))
items = os.listdir(base_dir)
package_name = next((item for item in items if os.path.isdir(os.path.join(base_dir, item)) and not item.startswith("__") and item != "tests"), None)

if not package_name:
    raise Exception("Package directory not found.")

version_path = os.path.join("tests", "version.txt")
readme_path = os.path.join("README.md")

setup(
    name=package_name,
    version=open(version_path).read().strip(),
    author="Back",
    description="A python library for creating simple GUI with pygame.",
    long_description=open(readme_path).read(),
    long_description_content_type="text/markdown",
    license="GPL-3.0-or-later",
    license_files=["LICENSE"],
    packages=find_packages(),
    install_requires=["pygame"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
