# saePy

**saePy** is a Python package for Small Area Estimation (SAE) implementing the EBLUP Fay-Herriot (FH), Nested Error Regression (BHF), and spatial Fay-Herriot (SFH) models. It also provides functions for estimating Mean Squared Error (MSE) and parametric bootstrap MSE for these models.

## Features

- **EBLUP Fay-Herriot (FH):** Area-level small area estimation.
- **EBLUP Nested Error Regression (BHF):** Unit-level small area estimation.
- **EBLUP Spatial Fay-Herriot (SFH):** Area-level model with spatial correlation.
- **MSE Estimation:** Functions to estimate the mean squared error for FH and SFH models.
- **Parametric Bootstrap MSE for BHF:** Bootstrap-based MSE estimation for the BHF model.
- **Example Datasets:** Several example datasets are included in the `saePy/` directory.

## Installation

Make sure you have the following dependencies installed:
- numpy
- scipy
- pandas
- patsy
- statsmodels

Install the package using:

```sh
pip install saePy
```
or
```sh
python setup.py install
```

## Directory Structure

```
saePy/
    __init__.py
    eblupBHF.py
    eblupFH.py
    eblupSFH.py
    mseFH.py
    mseSFH.py
    pbmseBHF.py
    dataset_1.csv
    grapes.csv
    grapesprox.csv
    unit_level_1.csv
```

## Usage

### EBLUP Fay-Herriot

```python
from saePy.eblupFH import eblupFH
import pandas as pd

data = pd.read_csv("saePy/dataset_1.csv")
result = eblupFH(
    formula="y ~ x1 + x2",
    vardir_col="vardir",
    data=data
)
print(result)
```

### EBLUP BHF (Unit Level)

```python
from saePy.eblupBHF import eblupBHF

result = eblupBHF(
    formula="y ~ x1 + x2",
    dom="domain",
    selectdom=[...],           # list of domains to estimate
    meanxpop=...,              # population mean matrix
    popnsize=...,              # population size per domain
    data=data
)
print(result)
```

### MSE Estimation

```python
from saePy.mseFH import mseFH

result = mseFH(
    formula="y ~ x1 + x2",
    vardir_col="vardir",
    data=data
)
print(result)
```

### Parametric Bootstrap MSE for BHF

```python
from saePy.pbmseBHF import pbmseBHF

result = pbmseBHF(
    formula="y ~ x1 + x2",
    dom="domain",
    selectdom=[...],
    meanxpop=...,
    popnsize=...,
    data=data
)
print(result)
```

## License

MIT License

---

**Note:**  
- Ensure your data columns match the function arguments.
- For more details, see the documentation in each module in [saePy/](saePy/).
