from setuptools import setup, find_packages

setup(
    name="mth308lib",
    version="1.0.0",
    description="A Python library implementing core numerical methods for MTH308: root-finding, linear systems, interpolation, and ODE solvers.",
    author="Tanish Bansal, Shobhit Goel",
    author_email="btanish23@iitk.ac.in, shobhitg23@iitk.ac.in",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)