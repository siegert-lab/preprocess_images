from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='preprocess_images',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements
    ,
    dependency_links=[
        'file:///path/to/third_party/aicspylibczi#egg=aicspylibczi',
    ],
)
