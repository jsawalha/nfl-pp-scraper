import pandas as pd
import numpy as np
import logging
import os
import glob
import re
import math
import json
from pandas.api.types import is_numeric_dtype

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def preprocess_data(df=None, position=None):

    if df.empty or df.shape[1] != 25:
        raise ValueError("Dataframe has wrong number of columns or does not exist")

    # Remove all `-` in the dataframe, replace with NaN
    df.replace("-", np.nan, inplace=True)

    # Position
    convert_nan("position", df)
    df["position"] = df["position"].apply(lambda x: remove_str(x))

    # Team
    df["team"], team_idx = factorize_col(
        "team", df, sorting=False, save=True, pos=position
    )

    # Draft
    df["draft"] = (
        df["draft"]
        .str.lower()
        .replace("undrafted", "0")
        .apply(lambda x: decimal_check(x))
    )
    convert_nan("draft", df)
    df["draft"] = df["draft"].astype(float)

    # College
    convert_nan("college", df)
    df["college"], col_idx = factorize_col(
        "college", df, sorting=False, save=True, pos=position
    )

    # Others
    rest_of = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    convert_multi_nan(rest_of, df)


def load_csv(position):
    if position not in ("quarterback", "wide-receiver", "running-back", "tight-end"):
        return ValueError("position does not exist. Must be one of the four positions")

    in_path = "../scraping/scraped_data/"

    if not os.path.isdir(in_path):
        raise ValueError("scraped data path does not exist in scraping folder")

    file = sorted(
        [f for f in os.listdir(in_path) if f.startswith("nfl_stats-" + position)],
        reverse=True,
    )[0]

    df = pd.read_csv(in_path + file, index_col=False)
    df.reset_index(drop=True, inplace=True)

    return df


def remove_str(x):
    return int(re.sub("[^0-9]", "", x))


def fill_na_zero(col, str_flag=False, int_flag=False):
    if str_flag:
        return col.fillna("None", inplace=True)
    elif int_flag:
        return col.fillna(-1, inplace=True)
    else:
        return col.fillna("0", inplace=True)


def convert_nan(pd_col_str, df):

    pd_col = get_column(pd_col_str, df)

    if isinstance(pd_col, float):
        fill_na_zero(pd_col)
    elif isinstance(pd_col, object):
        fill_na_zero(pd_col)
    else:
        raise ValueError("Cannot convert NaN. Column not a float64 or object")


def decimal_check(x):

    if float(x).is_integer():
        return "0"
    else:
        return x


def get_column(col_name, dataframe):
    return dataframe[col_name]


def convert_multi_nan(pd_col_str, df):

    pd_col = get_column(pd_col_str, df)
    pd_col = pd_col.astype(float)

    for cl in pd_col:
        if is_numeric_dtype(df[cl]):
            fill_na_zero(df[cl], int_flag=True)
        else:
            raise ValueError("Cannot convert NaN. Column not a float64 or object")


def factorize_col(pd_col_str, df, sorting=False, save=False, pos=None):

    pd_fac, pd_idx = get_column(pd_col_str, df).factorize(sort=sorting)

    if save:
        fact_dict = dict(zip(range(len(pd_idx)), pd_idx))
        dict_path = "preprocessed_data/dicts/" + pos + "-" + pd_col_str + ".txt"
        with open(dict_path, "w") as file:
            file.write(json.dumps(fact_dict))

    return pd_fac, pd_idx


def save_csv(position, df):
    if position not in ("quarterback", "wide-receiver", "running-back", "tight-end"):
        return ValueError("position does not exist. Must be one of the four positions")

    out_path = "../preprocessing/preprocessed_data/"

    if not os.path.isdir(out_path):
        os.mkdir(out_path)
        raise Warning("preprocessed data path does not exist in preprocessing folder")

    OUTPUT = out_path + "preprocessed_" + position + ".csv"

    df.to_csv(OUTPUT, index=False)

    logging.info(f"Saving preprocessed csv file for the {position} position")
    logging.info("Done")
