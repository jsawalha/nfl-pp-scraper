import pandas as pd
import numpy as np
import logging
import os
import glob
import re
import math
from pandas.api.types import is_numeric_dtype


def load_csv(position):
    if position not in ("quarterback", "wide-receiver", "running-back", "tight-end"):
        return ValueError("position does not exist. Must be one of the four positions")

    in_path = "scraping/scraped_data/"

    if not os.path.isdir(in_path):
        raise ValueError("scraped data path does not exist in scraping folder")

    file = sorted([f for f in os.listdir(in_path) if f.startswith('nfl_stats-' + position)],
                   reverse=True)[0]

    df = pd.read_csv(in_path + file, index_col=False)
    df.reset_index(drop=True, inplace=True)
    
    return df


def remove_str(x):
    return int(re.sub('[^0-9]','', x))

def fill_na_zero(col, str_flag = False, int_flag = False):
    if str_flag:
        return col.fillna('None', inplace=True)
    elif int_flag:
        return col.fillna(-1, inplace=True)
    else:
        return col.fillna('0', inplace=True)

def convert_nan(pd_col_str, df):

    pd_col = df[pd_col_str]

    if isinstance(pd_col, float):
        fill_na_zero(pd_col)
    elif isinstance(pd_col, object):
        fill_na_zero(pd_col)
    else:
        raise ValueError("Cannot convert NaN. Column not a float64 or object")

        
def draft_decimal_check(x):

    if float(x).is_integer():
        return '0'
    else:
        return x


def convert_multi_nan(pd_col_str, df):

    pd_col = df[pd_col_str]
    pd_col = pd_col.astype(float)

    for cl in pd_col:
        if is_numeric_dtype(df[cl]):
            fill_na_zero(df[cl], int_flag=True)
        else:
            raise ValueError("Cannot convert NaN. Column not a float64 or object")
