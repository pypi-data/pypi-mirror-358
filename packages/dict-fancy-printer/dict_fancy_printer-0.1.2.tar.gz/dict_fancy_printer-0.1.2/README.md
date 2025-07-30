# dict-fancy-printer

A simple library to print Python dictionaries in a fancier and more understandable way.

## Installation

To install from pip:
```bash
pip install dict-fancy-printer
```

To install directly from the master branch, use:
```bash
pip install git+https://github.com/matteogabburo/dict-fancy-printer
```

If you want to install a specific development branch, use:
```bash
pip install git+https://github.com/matteogabburo/dict-fancy-printer@<branch_name>
```

## Usage

### FancyPrinter
- Example:
```python
from dict_fancy_printer import FancyPrinter
printer = FancyPrinter()

d = {
  "driver": "Marty McFly",
  "vehicle": "DeLorean",
  "speed_mph": 88,                           
  "flux_capacitor": True,                     
  "last_departure": "1985-11-05 16:29:00",
  "quote": "Great Scott!",
}

print(printer(d))
```

### print_fancy_dict
- Example:
```python
from dict_fancy_printer import print_fancy_dict

d = {
"driver": "Marty McFly",
"vehicle": "DeLorean",
"speed_mph": 88,                           
"flux_capacitor": True,                     
"last_departure": "1985-11-05 16:29:00",
"quote": "Great Scott!",
}

print_fancy_dict(d)
```

### fancy_dict
- Example:
```python
from dict_fancy_printer import fancy_dict

d = {
"driver": "Marty McFly",
"vehicle": "DeLorean",
"speed_mph": 88,                           
"flux_capacitor": True,                     
"last_departure": "1985-11-05 16:29:00",
"quote": "Great Scott!",
}

d = fancy_dict(d)
print(d)
```