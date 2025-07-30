from setuptools import setup, find_packages
import os

# Use the outer README.md for PyPI long_description
this_dir = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_dir, "README.md")

with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='kotlinwrapper',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={'kotlinwrapper': ['README.md']},  # Inner README will be bundled
    long_description=long_description,
    long_description_content_type='text/markdown',
)
