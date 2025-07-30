from setuptools import setup, find_packages

setup(
    name="ngd",
    version="0.2.1",
    packages=find_packages(),
    install_requires=[
        "biopython>=1.79",
        "matplotlib>=3.5.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "requests>=2.25.0"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive bioinformatics package with 10 essential programs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ngd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
    ],
    python_requires=">=3.7",
    keywords="bioinformatics, dna, rna, protein, sequence, alignment, phylogenetics",
) 