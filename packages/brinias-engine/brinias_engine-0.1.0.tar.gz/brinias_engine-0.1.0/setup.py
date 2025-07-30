# setup.py

from setuptools import setup, find_packages

setup(
    name="brinias-engine", 
    version="0.1.0",
    author="Konstantinos Brinias",
    author_email="brinias2@gmail.com",
    description="Brinias: A symbolic regression and classification tool using Genetic Programming.", 
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/brinias/brinias", 
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "deap",
        "matplotlib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)