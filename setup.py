# setup.py
from setuptools import setup, find_packages

setup(
    name="noise-adaptive-depth-probe",
    version="0.1.0",
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    author="Jeorge D. Anderson II",
    description="Empirical depth threshold characterization for ADQNN-GAGE",
    python_requires='>=3.9',
)