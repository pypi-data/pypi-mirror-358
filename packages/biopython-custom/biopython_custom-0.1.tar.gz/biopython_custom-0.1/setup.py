from setuptools import setup, find_packages

setup(
    name='biopython-custom',      # Use a unique name to avoid conflict with real 'biopython'
    version='0.1',
    packages=find_packages(),     # Finds 'biopython' folder
    install_requires=[],
    author='Your Name',
    description='Custom tools for bioinformatics',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
