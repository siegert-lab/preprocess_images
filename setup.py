from setuptools import setup, find_packages

setup(
    name='preprocess_images',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'imaris_ims_file_reader',
        'numpy==2.2.2',
        'packaging==24.2',
        'pandas==2.2.3',
        'pillow==11.1.0',
        'plotly==5.24.1',
        'python-dateutil==2.9.0.post0',
        'pytz==2024.2',
        'six==1.17.0',
        'tenacity==9.0.0',
        'tifffile==2025.1.10',
        'tzdata==2025.1',
        'ipykernel==6.25.1',
        'paramiko==3.2.0',
        'nbformat>=4.2.0',
    ],
    dependency_links=[
        'file:///path/to/third_party/aicspylibczi#egg=aicspylibczi',
    ],
)
