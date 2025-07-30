# ZoneFinder

## Description

`zonefinder` is a Python package designed to identify and analyze key support and resistance price levels 
from financial market data.

It provides tools to detect the most frequent highs, lows, and closes, as well as to cluster these price points into support and resistance zones.

## Installation

You can install `zonefinder` via pip:

```bash
pip install zonefinder
```

## Usage
Here is a simple example to identify frequent price levels from your price data:
```python
import pandas as pd
from zonefinder import identify_frequent_price_levels, identify_support_resistance_zones

# Load your price data, must contain columns 'high', 'low', and 'close'
data = pd.read_csv('your_price_data.csv')

# Identify and Print the top 5 most frequent price levels
levels = identify_frequent_price_levels(data, rounding_digits=2, show_output=True)

# Detect the top 10 most frequent support and resistance zones with default epsilon = 0.1
zones = identify_support_resistance_zones(data, top_n=10, epsilon=0.1, show_output=True)
```

## Author

Anthony Gocmen - [email](mailto:anthony.gocmen@gmail.com)  
WebSite: [developexx](https://www.developexx.com)


## License


This project is licensed under the MIT License - see [MIT](https://choosealicense.com/licenses/mit/) for details.