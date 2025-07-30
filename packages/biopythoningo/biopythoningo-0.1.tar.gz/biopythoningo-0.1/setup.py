from setuptools import setup, find_packages

setup(
    name='biopythoningo',                  # This is the name others will install
    version='0.1',
    packages=find_packages(),             # Includes 'sujan' and subfolders with __init__.py
    install_requires=[],
    author='meow',
    description='All of meow\'s custom bioinformatics tools',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
