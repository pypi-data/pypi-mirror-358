from setuptools import setup, find_packages

setup(
    name='NetDecom',  # Package name
    version='0.0.5.0',  # Version number
    description='Dimensionality Reduction and Decomposition of Undirected Graph Models and Bayesian Networks',  # Package description
    author='Hugh',  # Author name
    # author_email='',  # Author email (optional)
    packages=find_packages(),  # Find all packages
    long_description=open('README.md').read(),  # Read detailed description from README.md
    long_description_content_type='text/markdown',  # Specify the format of the README file
    classifiers=[  # Choose appropriate classifiers
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',  # Compatible with Python 3.9
        'License :: OSI Approved :: MIT License',  # License type
        'Operating System :: OS Independent',  # Cross-platform
    ],
    package_data={  # Ensure the examples folder is included
        'NetDecom': ['examples/*'],  # Include all files under the examples folder
    },
    include_package_data=True,  # Ensure package data is included
)
