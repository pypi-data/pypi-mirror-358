import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dwight_schrute",                     # This is the name of the package
    version="0.0.24",                        # The initial release version
    author="Hitesh Gulati",                     # Full name of the author
    description="If Dwight Schrute was a Data Analysts he would have used this Library",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["dwight_schrute"],             # Name of the python package
    package_dir={'':'dwight_schrute/src'},     # Directory of the source code of the package
    install_requires=[]                     # Install other dependencies if any
)