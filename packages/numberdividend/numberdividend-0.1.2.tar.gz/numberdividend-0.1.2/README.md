# NumberDividend

A simple Python package to split a list of numbers so that their sum matches a target value.

## Installation
```bash
pip install numberdividend
```
## Usage
You can use it as a module:
```python
from numberdividend import NumberCore

array = [1, 2, 3, 5, 6]

div = NumberCore.dividend(array, 900, 3, 5)
NumberCore.display(div)
```
___
```python
NumberCore.dividend(array, target_sum, limit, decimal)
```
Calculate the dividend distribution of an array.
| Value | Type | Description |
|--|--|--|
| array | List[float] | List of float numbers to be distributed. |
| target_sum | float | Target sum for the distribution. |
| limit | int, optional | Maximum number of elements to consider from the array. |
| decimal | int, optional | Number of decimal places for the output. |
| return | List[Tuple[float, float]] | List of tuples containing the index and the dividend value |
___
```python
NumberCore.display(array)
```
Display the dividend distribution using matplotlib.
| Value | Type | Description |
|--|--|--|
| array | List[float] | List of dividend values to be displayed. |
___
### CLI Usage
```bash
python -m numberdividend C:\User\path\...\input.csv 300 C:\User\path\...\output.csv --limit 30 --display
```
⚠️ Only `.csv` files are supported as input.
Structure of `input.csv`:
| No column name |
|--|
| 1 |
| 2 |
| 3 |
| 5 |
| 9 |
___
Command struct
| Value | Type | Description |
|--|--|--|
| path | str | Input file path |
| target | int | Value of sum the array |
| save | str | Output file path |
| --limit | int | Optional limit on the number of elements considered |
| --display | none | Optional displays the processed array |
### License
MIT
### Author
Sabolch - [Github profile](https://github.com/SaboIch)
