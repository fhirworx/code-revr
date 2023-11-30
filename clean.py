import os
import re
import pandas as pd
import zipfile

def remove_blank_rows_and_cols(df):
    df = df.dropna(how='all')
    df = df.dropna(axis=1, how='all')
    return df

def convert_to_snake_case(name):
    name = re.sub(r'-', '_', name)  # Remove hyphens and replace with underscores
    name = name.lstrip()  # Remove leading spaces
    name = re.sub(r'\s+', '_', name)  # Replace spaces with underscores
    name = name.lower()  # Convert to lower case
    name = name.strip('_')  # Remove underscores at the beginning or end
    name = re.sub(r'^\d{4}_', '', name)  # Remove leading YYYY_
    return name

def find_header_and_concatenate_df(df):
    header = df.iloc[0].tolist()
    for i in range(1, len(df)):
        row = df.iloc[i].tolist()
        header = [h + ' ' + str(r) if str(r) != '' else h for h, r in zip(header, row)]
        non_blank_columns = len([col for col in header if col != ''])
        if non_blank_columns == len(row):
            return i, header
    return None, None

def infer_datatypes(df, sample_size):
    sample_df = df.sample(n=min(sample_size, df.shape[0]), random_state=1)
    inferred_df = sample_df.infer_objects()
    dtypes = inferred_df.dtypes.to_dict()
    for col, dtype in dtypes.items():
        try:
            df[col] = df[col].astype(dtype)
        except ValueError:
            continue
    return df, dtypes

def process_dataframe(df):
    try:
        row_index, header = find_header_and_concatenate_df(df)
        if row_index is not None:
            df = df.iloc[row_index+1:]
            df.columns = header
            df, _ = infer_datatypes(df, sample_size=1000)
            df = remove_blank_rows_and_cols(df)
            df.columns = [convert_to_snake_case(col) for col in df.columns]
    except Exception as e:
        print(f'Failed to process DataFrame, error: {str(e)}')
    return df