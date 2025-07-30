""" This is test for my package """

from src.zonefinder.core import identify_frequent_price_levels, identify_support_resistance_zones

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd


mt5.initialize(login=5036923188, server="MetaQuotes-Demo", password="Wi*qR5Zm")

# Initialize Parameters
SYMBOL = "USTEC"
timeframe = mt5.TIMEFRAME_M5

# Fetch data
rates = mt5.copy_rates_from(SYMBOL, timeframe, datetime.now(), 10000)
df = pd.DataFrame(rates, columns=['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume'])
df['time'] = pd.to_datetime(df['time'], unit='s')



mt5.shutdown()

x = identify_support_resistance_zones(df, show_output=True, chain_comparison=True)




