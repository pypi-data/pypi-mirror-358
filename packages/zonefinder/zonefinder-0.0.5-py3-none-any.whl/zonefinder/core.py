from collections import Counter
import pandas as pd
from typing import Dict, List, Tuple


def _validate_inputs(
    dataframe: pd.DataFrame,
    columns: list[str],
    rounding_digits: int,
    top_n: int,
) -> None:
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame for argument 'dataframe'.")

    for column in columns:
        if column not in dataframe.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame. Please provide a valid column name.")

    if not isinstance(rounding_digits, int) or rounding_digits < 0:
        raise ValueError("The 'rounding_digits' parameter must be a non-negative integer.")

    if not isinstance(top_n, int) or top_n <= 0:
        raise ValueError("The 'top_n' parameter must be a positive integer.")




def identify_frequent_price_levels(
        dataframe: pd.DataFrame,
        high_col: str = 'high',
        low_col: str = 'low',
        close_col: str = 'close',
        top_n: int = 5,
        rounding_digits: int = 2,
        show_output:bool = False
) -> Dict[str, List[Tuple[float, int]]]:

    """
    Identifies the most frequent price levels in the given financial data for highs, lows, and closes.

    Parameters
    -------
    dataframe : pd.DataFrame
        Input DataFrame containing price data
    high_col : str, optional
        Name of the high price column (default 'high')
    low_col : str, optional
        Name of the low price column (default 'low')
    close_col : str, optional
        Name of the close price column (default 'close')
    rounding_digits : int, optional
        Number of decimal places to round to (default 2)
    top_n : int, optional
        Number of top levels to return (default 5)
    show_output : bool, optional
        Whether to print results (default False)

    Returns
    -------
    Dict[str, List[Tuple[float, int]]]
        A dictionary with the following keys:

        - 'highs' : List of (price, count) tuples for highs.
        - 'lows' : List of (price, count) tuples for lows.
        - 'closes' : List of (price, count) tuples for closes.
        - 'all_levels' : List of (price, count) tuples for all combined levels.
    """

    _validate_inputs(
        dataframe=dataframe,
        columns=[high_col, low_col, close_col],
        top_n=top_n,
        rounding_digits=rounding_digits
    )

    rounded_high = dataframe[high_col].dropna().round(rounding_digits)
    rounded_low = dataframe[low_col].dropna().round(rounding_digits)
    rounded_close = dataframe[close_col].dropna().round(rounding_digits)


    all_counter = Counter(rounded_high) + Counter(rounded_low) + Counter(rounded_close)
    high_counter = Counter(rounded_high)
    low_counter = Counter(rounded_low)
    close_counter = Counter(rounded_close)


    frequent_highs = high_counter.most_common(top_n)
    frequent_lows = low_counter.most_common(top_n)
    frequent_closes = close_counter.most_common(top_n)
    frequent_global =  all_counter.most_common(top_n)


    if show_output:
        print(f"---- FREQUENT PRICE LEVELS (rounded to {rounding_digits})----\n")
        print(f"\n=== Top {top_n} Most Frequent Highs ===")
        for level, count in frequent_highs:
            print(f"Price: {level:.{rounding_digits}f}  |  Occurrence: {count}")

        print(f"\n=== Top {top_n} Most Frequent Lows ===")
        for level, count in frequent_lows:
            print(f"Price: {level:.{rounding_digits}f}  |  Occurrence: {count}")

        print(f"\n=== Top {top_n} Most Frequent Closes ===")
        for level, count in frequent_closes:
            print(f"Price: {level:.{rounding_digits}f}  |  Occurrence: {count}")

        print(f"\n=== Top {top_n} Most Frequent Price Levels (Combined) ===")
        for level, count in frequent_global:
            print(f"Price: {level:.{rounding_digits}f}  |  Occurrence: {count}")


    return {
        'highs': frequent_highs,
        'lows': frequent_lows,
        'closes': frequent_closes,
        'all_levels': frequent_global
    }


#_______________________________________________________________________________________________________________


def identify_support_resistance_zones(
        dataframe: pd.DataFrame,
        high_col: str = 'high',
        low_col: str = 'low',
        close_col: str = 'close',
        epsilon: float = 0.1,
        chain_comparison: bool = True,
        top_n: int = 5,
        rounding_digits: int = 2,
        show_output: bool = False
) -> Dict[str, pd.DataFrame]:

    """
    Detects clusters of price levels that are within a specified proximity (epsilon) and form potential support or resistance zones.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Input DataFrame containing price data.
    high_col : str, optional
        Name of the column for high prices (default 'high').
    low_col : str, optional
        Name of the column for low prices (default 'low').
    close_col : str, optional
        Name of the column for close prices (default 'close').
    epsilon : float, optional
        Maximum allowed price difference to consider prices part of the same zone (default 0.1).
    chain_comparison : bool, optional
        If True (default), each price is compared to the last price in the current zone, allowing zones to grow gradually.
        If False, each price is compared to the first price in the zone, making zones more strict and uniform.
    top_n : int, optional
        Number of top levels to return (default 5)
    rounding_digits : int, optional
        Number of decimal places to round mean prices in the zones (default 2).
    show_output : bool, optional
        Whether to print the detected zones for each price type (default False).

    Returns
    -------
    Dict[str, pd.DataFrame]
        A dictionary containing DataFrames of detected zones for each price type:

            - 'highs': Zones detected from high prices.
            - 'lows': Zones detected from low prices.
            - 'closes': Zones detected from close prices.
            - 'all_levels': Zones detected from combined price points of all three types.
    """

    _validate_inputs(
        dataframe=dataframe,
        columns=[high_col, low_col, close_col],
        top_n=top_n,
        rounding_digits=rounding_digits
    )

    if epsilon <= 0:
        raise ValueError("The 'epsilon' parameter must be positive.")


    rounded_high = dataframe[high_col].round(rounding_digits).dropna().tolist()
    rounded_low = dataframe[low_col].round(rounding_digits).dropna().tolist()
    rounded_close = dataframe[close_col].round(rounding_digits).dropna().tolist()
    all_prices = rounded_high + rounded_low + rounded_close


    def _extract_zones(price_list):
        if not price_list:
            return []
        sorted_prices = sorted(price_list)
        zones = []
        current_zone = [sorted_prices[0]]
        if chain_comparison:
            for price in sorted_prices[1:]:
                if abs(price - current_zone[-1]) <= epsilon:
                    current_zone.append(price)
                else:
                    zones.append(current_zone)
                    current_zone = [price]
            zones.append(current_zone)
        else:
            for price in sorted_prices[1:]:
                if abs(price - current_zone[0]) <= epsilon:
                    current_zone.append(price)
                else:
                    zones.append(current_zone)
                    current_zone = [price]
            zones.append(current_zone)

        return pd.DataFrame([
            {
                'zone_min': min(zone),
                'zone_max': max(zone),
                'mean_price': round(sum(zone) / len(zone), rounding_digits),
                'count': len(zone)
            }
            for zone in zones
        ])


    zones_high = _extract_zones(rounded_high)
    zones_low = _extract_zones(rounded_low)
    zones_close = _extract_zones(rounded_close)
    zones_all = _extract_zones(all_prices)

    if show_output:
        def _print_zones(df, label):
            if chain_comparison:
                print(f"---- FREQUENT SUPPORT|RESISTANCE ZONES (Chain Comparison) ----\n")
            else:
                print(f"---- FREQUENT SUPPORT|RESISTANCE ZONES (Base Comparison) ----\n")
            print(f"\n====== Top {top_n} Support/Resistance Zones for {label} ======")
            if df.empty:
                print("No zones detected.")
                return
            df = df.sort_values(by='count', ascending=False).head(top_n)
            for idx, row in df.iterrows():
                print(
                    f"Zone: {row['zone_min']:.{rounding_digits}f} - {row['zone_max']:.{rounding_digits}f} | "
                    f"Spread: {( row['zone_max'] - row['zone_min']):.{rounding_digits}f} | "
                    f"Mean: {row['mean_price']:.{rounding_digits}f} | Count: {row['count']:.0f}")

        _print_zones(zones_high, 'Highs')
        _print_zones(zones_low, 'Lows')
        _print_zones(zones_close, 'Closes')
        _print_zones(zones_all, 'All Levels')

    return {
        'highs': zones_high,
        'lows': zones_low,
        'closes': zones_close,
        'all_levels': zones_all
    }



