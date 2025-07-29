# ITk PDB Reportorium

A common repository for shared reporting tools for ITk PDB data:

 - common code to help make reports

 - documentation on _common_ reporting

Existing ITk reports can be found [ITk PDB Reporting Hub](https://itk-pdb-reporting-hub.docs.cern.ch)


## Common code 

Common code to help make reports in *common_code* directory:

__flattening__ 

  - functions for flattening data from ITk PDB
  - examples to make it easier to navigate PDB data-structure

__visualisation__ 

  - functions for *standard* visualisations
  - examples to make to provide basic plot styles

__distribution__

  - functions for setting-up and distributing reports 
  - examples for collation of PDB information and sharing


## Tutorial

__Example workflow__

- example of steps to publish report

## 📦 Package Release

To release a new version of the package, follow these steps:

1. **Clean previous builds**  
   Remove any existing build artifacts to ensure a clean release:
   ```bash
   rm -rf dist/ build/ *.egg-info
2. **An important step**  
The number of the version in the setup should be updated for the next version.

3. **Build the package**  
Generate the source and wheel distributions:  
   ```bash
   python setup.py sdist bdist_wheel
4. **Upload the newly built distributions using twine**  
   ```bash
   twine upload dist/*
5. **The Package credentials**
   ```bash
    pypi-AgEIcHlwaS5vcmcCJGVjMmE4ZGUxLTU2ZjMtNDZjOC1hY2Y0LTZhMjcwOGJkMzlmNwACKlszLCIzMTdjZGVjMi1hMDEwLTRlZjEtOGQzYy1lYjg5NTYxODdhMTEiXQAABiCWPW5GwB1lMN-JFkUJo-wyIXK-7-QU2WN0cVNeLsKNfA
