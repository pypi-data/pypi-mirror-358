# LightImpact
[![PyPI version](https://badge.fury.io/py/lightimpact.svg?v=0.1.2)](https://pypi.org/project/lightimpact/0.1.2/)

**LightImpact** is an open-source Python library for calculating the **Energy Reduction Value (ERV)** of lightweight automotive components applied in both internal combustion vehicles (ICVs) and electric vehicles (EVs), based on WLTP driving cycle data.
Developed for life cycle assessment (LCA) modeling in the **MM4R** research project at RWTH Aachen University.

## Features
- Physics-based mechanical work calculation
- WLTP-compliant ERV computation
- Compatible with both ICVs and EVs
- Customizable input parameters
- Suitable for integration into LCA workflows

## Installation
```bash
git clone https://github.com/suzanaostojic/LightImpact-MM4R.git
cd LightImpact-MM4R
pip install -e .
```

## Example Usage
```python
from lightimpact.core import run_lightimpact_case

custom_params = {
    "m_vehicle": 1800,
    "cw": 0.28,
    "A_frontal": 2.3,
    "ds": 25.0,
    "c_fuel_WLTP": 9.5
}

run_lightimpact_case("WLTP_data/Time-Speed-Profile_WLTP_Class3b.csv", custom_params)
```

## License
Licensed under the MIT License (c) 2025 Suzana Ostojic

## About
LightImpact was developed for use within the MM4R research project at the RWTH Aachen University.  
Contact: [suzana.ostojic@inab.rwth-aachen.de](mailto:suzana.ostojic@inab.rwth-aachen.de)
GitHub: [github.com/suzanaostojic/LightImpact-MM4R](https://github.com/suzanaostojic/LightImpact-MM4R)  
PyPI: [pypi.org/project/lightimpact](https://pypi.org/project/lightimpact)