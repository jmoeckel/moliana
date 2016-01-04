# Moliana
A Python written **MO**delica **LI**brary **ANA**lyser for Dymola.

## Overview
Analysation of modelica libraries based on Dymolas `checkModel()`.

In Dymola, `checkModel()` could only be applied to one package/model at a time. Forthermore and unfortunately, results of `checkModel()` for one package/model are discarded after applying `checkModel()` to the next package/model.

Moliana enables the user to apply `checkModel()` to a complete library (or only selected packages) and get results for each subpackage/submodel up to a chosen level.

Results of `checkModel()` are reduced to the number of errors and warnings and the overall result (success of failure). These results can be converted to a table-based Html code, with the possibility to highlight failures, errors or warnings.

Furthermore it is possible to compare one set of results to a different one (as long as both sets correspond to the same library) and highlight changes with respect to the numbers of errors or warnings or the overall result.  
Of course this could be used for different usecases, but its main purpose is the usecase of software development using versioning systems as git or svn and to ease the process of assuring quality when merging development branches to the master.  

Moliana provides following classes:
* `DymolaMode`: Automated execution of Dymolas `checkModel()`.
* `Report`: Representation and comparison of results.
* `Converter`: Conversion of Report instances to HTML files and vice versa.

## Usage of Moliana
The following lines show a general usage of Moliana.
```
pDym = os.path.join('C:\Program Files (x86)\Dymola 2016\\bin64','Dymola.exe')
pLib = os.path.join('examples',TestModelicaLibrary')
pRep = os.path.join('examples',reports')
dlc = moliana.DymolaMode(pLib, pDym, report_name ='example', report_path = pRep)            
dlc.execute_check('html')
```
This will apply `DymolaMode` to the Modelica library `TestModelicaLibrary`. An Html report with file name `example.html` is generated in the folder `reports`. Both, the folder `reports` as well as the library are stored in the folder `examples`.

More examples, especially one that shows how to compare reports, can be found in [`./examples/examples.py`](https://github.com/jmoeckel/moliana/blob/master/examples/examples.py) or in the [Examples](https://github.com/jmoeckel/moliana/wiki/Examples) section of the  [wiki](https://github.com/jmoeckel/moliana/wiki).

## Documentation of the API
Take a look at the [source code](https://github.com/jmoeckel/moliana/blob/master/moliana.py) of Moliana or at the [wiki](https://github.com/jmoeckel/moliana/wiki). In both places, the complete user-interface of Moliana is documented.

## Software Requirements
* This module has been implemented and tested with Python 3.4.3 on a Windows 7 and Windows 10 platform.
* DymolaMode requires Dymola 2016 or newer.

## License
Moliana comes along with a GNU General Public License (see file [`LICENSE.txt`](https://github.com/jmoeckel/moliana/blob/master/LICENSE.txt)). Additional information can be found in the header of [`moliana.py`](https://github.com/jmoeckel/moliana/blob/master/moliana.py).
