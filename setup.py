from setuptools import setup, find_packages
import sys

# Check Python version
if sys.version_info < (3, 10):
    print("ERROR: preprocess_images requires Python 3.10 or above.")
    print("Tip: Create a conda environment with: conda create -n preprocess-img python=3.10")
    sys.exit(1)

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Filter out comments from requirements
requirements = [req for req in requirements if not req.startswith('#') and req.strip()]

# Add bdv_toolz to requirements if not already present
if 'bdv_toolz' not in requirements:
    requirements.append('bdv_toolz')

setup(
    name='preprocess_images',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.10',
    install_requires=requirements,
    dependency_links=[
        'file:third_party/aicspylibczi#egg=aicspylibczi',
        'git+https://git.ista.ac.at/csommer/bdv_toolz.git#egg=bdv_toolz',
    ],
)
