from setuptools import setup, find_packages

setup(
    name="itk-pdb-reportorium",
    version="0.1.14",
    packages=find_packages(where="."),
    description=(
        "A common repository for shared reporting tools for ITk PDB data:\n\n"
        "common code to help make reports\n\n"
        "documentation on common reporting"
    ),

    author="kenneth wraight, Omar Istaitia, Doyeong Kim, Dimitris Varouchas",
    author_email=(
        "kenneth.wraight@glasgow.ac.uk, omar.istaitia@cern.ch, "
        "doyeong.kim@cern.ch, dimitris.varouchas@cern.ch"
    ),
    install_requires=[
        "randomname",
        "scp",
        "paramiko",
    ],
    include_package_data=True,  
    package_data={
        "common_code": ["metadata/*.json"],  # <-- relative to the common_code package
    },
)
