from setuptools import setup, find_packages

setup(
    name="saePy",
    version="0.2.1",
    description="Small Area Estimation Python package",
    author="Agus Riyanto",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "polars",
        "patsy"
    ],
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)