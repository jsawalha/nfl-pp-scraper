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
    """
    Main preprocessing head function. This will sequentially alter all columns. Will convert
    NaN values, change data types, factorize strings, and prepare the dataframe for data analysis
    or machine learning

    Parameters
    ----------
    df (dataframe): the placeholder dataframe loaded from the args.parse position

    position (str): The NFL position that is being generated [`quarterback`, `running-back`, `wide-receiver`, `tight-end`]

    Returns
    --------
    pd.dataframe: A preprocessed version of the dataset

    """

    if df.empty or df.shape[1] != 25:
        raise ValueError("Dataframe has wrong number of columns or does not exist")

    # Remove all `-` in the dataframe, replace with NaN
    # Sometimes dashes exist in the scraping portion of the website
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

    # Others (different header column names for each )
    rest_of = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    convert_nan(rest_of, df, multi_flag=True)


def load_csv(position):
    """
    Loads csv file into the preprocessing pipeline

    Parameters
    ----------
    position (str): The NFL position that is being generated [`quarterback`, `running-back`, `wide-receiver`, `tight-end`]

    Returns
    --------
    pd.dataframe: A raw dataset based on position.
    """

    if position not in ("quarterback", "wide-receiver", "running-back", "tight-end"):
        return ValueError("position does not exist. Must be one of the four positions")

    in_path = "../scraping/scraped_data/"

    if not os.path.isdir(in_path):
        raise ValueError("scraped data path does not exist in scraping folder")

    # Takes the most recent file based on the date in the file name
    file = sorted(
        [f for f in os.listdir(in_path) if f.startswith("nfl_stats-" + position)],
        reverse=True,
    )[0]

    df = pd.read_csv(in_path + file, index_col=False)
    df.reset_index(drop=True, inplace=True)

    return df


def remove_str(x):
    """
    Removes and converts a string entry into an integer
    """
    return int(re.sub("[^0-9]", "", x))


def fill_na_zero(col, str_flag=False, int_flag=False):
    """
    Replaces NaN with certain values depending on the data type of the column.
    String columns will replace NaN values with `None`.
    Integer columns will replace NaN values with `-1`.
    Object, Float columns will replace NaN values with `0`.
    This is to ensure that all nan values are consistent with their column data type.

    Parameters
    ----------
    col(str): The name of the column in the dataset
    str_flag (bool): Whether the column is filled with strings
    int_flag (bool): Whether the column is filled with integers

    """

    if str_flag:
        return col.fillna("None", inplace=True)
    elif int_flag:
        return col.fillna(-1, inplace=True)
    else:
        return col.fillna("0", inplace=True)


def convert_nan(pd_col_str, df, multi_flag=False):
    """
    Checks to see if the column is a float or an object. This is done to determine how to fill NaNs for a given column

    Parameters
    ----------
    pd_col_str (str): The column name of the dataset
    df (dataframe): The current dataframe
    multi_flag (bool): whether you are converting multi columns at once, or not.

    """

    if multi_flag:
        pd_col = get_column(pd_col_str, df)
        pd_col = pd_col.astype(float)

        for cl in pd_col:
            if is_numeric_dtype(df[cl]):
                fill_na_zero(df[cl], int_flag=True)
            else:
                raise ValueError("Cannot convert NaN. Column not a float64 or object")

    else:

        pd_col = get_column(pd_col_str, df)

        if isinstance(pd_col, float):
            fill_na_zero(pd_col)
        elif isinstance(pd_col, object):
            fill_na_zero(pd_col)
        else:
            raise ValueError("Cannot convert NaN. Column not a float64 or object")


def decimal_check(x):
    """
    Checks to determine whether there is a decimal present in the variable. If there is, it returns a 0, if not,
    it returns the original value. This is done because some draft positions include the year
    instead of the draft position (1.02 (1st round, 2nd pick) vs. 2021).
    We are trying to impute all year values with 0, since we do not know their draft position.
    """

    if float(x).is_integer():
        return "0"
    else:
        return x


def get_column(col_name, dataframe):
    """
    Returns a column of data from the data frame.
    """
    return dataframe[col_name]


# def convert_multi_nan(pd_col_str, df):

#     pd_col = get_column(pd_col_str, df)
#     pd_col = pd_col.astype(float)

#     for cl in pd_col:
#         if is_numeric_dtype(df[cl]):
#             fill_na_zero(df[cl], int_flag=True)
#         else:
#             raise ValueError("Cannot convert NaN. Column not a float64 or object")


def factorize_col(pd_col_str, df, sorting=False, save=False, pos=None):
    """
    Factorizes column variables, converting them from recurring string to integers.

    Parameters
    ----------
    pd_col_str (str): The column name of the dataset
    df (dataframe): The current dataframe
    sorting (bool): Turn sorting on for the pd.factorize() function
    save (bool): Save the index of factorized names (saves inside `preprocessed_data` as a .txt file)
    pos (str): The NFL position [`quarterback`, `running-back`, `wide-receiver`, `tight-end`]


    Returns
    --------
    pd.Series: A pd.column that is factorized.

    """

    pd_fac, pd_idx = get_column(pd_col_str, df).factorize(sort=sorting)

    if save:
        fact_dict = dict(zip(range(len(pd_idx)), pd_idx))
        dict_path = "preprocessed_data/dicts/" + pos + "-" + pd_col_str + ".txt"
        with open(dict_path, "w") as file:
            file.write(json.dumps(fact_dict))

    return pd_fac, pd_idx


def save_csv(position, df):
    """
    Saves the preprocessed dataframe into `preprocessed_data`.

    Parameters
    ----------
    position (str): The NFL position that is being generated [`quarterback`, `running-back`, `wide-receiver`, `tight-end`]
    df (pd.Dataframe): The current dataframe being processed
    """

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
