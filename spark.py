import numpy as np
import pandas as pd
from pyspark.sql import DataFrame as PySparkDataFrame
from pyspark.sql import functions as F

# Helper function to determine if a DataFrame is PySpark or Pandas
def is_pyspark_df(df):
    return isinstance(df, PySparkDataFrame)

# Helper function to validate a given code ID.
def get_valid_code_id(code_id, df_column='code_id'):
    df = pfs.load_ruc()
    if is_pyspark_df(df):
        return code_id if df.filter(F.col(df_column) == code_id).count() > 0 else None
    else:
        return code_id if code_id in df[df_column].values else None

# Helper function to load data and filter by code ID.
def load_and_filter_df(code_id, load_function, column='hcpcs'):
    code_id = get_valid_code_id(code_id, df_column=column)
    if code_id:
        df = load_function()
        if is_pyspark_df(df):
            return df.filter(F.col(column) == code_id)
        else:
            return df[df[column] == code_id]
    return None

# Helper function to calculate total values.
def calculate_totals(df, time_columns, price_column, time_factor):
    if is_pyspark_df(df):
        for time_column in time_columns:
            df = df.withColumn(f'tot_{time_column}', F.col(time_column) * time_factor)
    else:
        for time_column in time_columns:
            df[f'tot_{time_column}'] = df[time_column] * time_factor
    return df

# Function to get current intensity values.
def get_current_intensity(code_id):
    df = load_and_filter_df(code_id, pfs.load_ruc, 'code_id')
    if df is not None:
        if is_pyspark_df(df):
            row = df.first()
            return tuple(row[col] for col in ['global_value', 'current_tt', 'current_ist', 'current_preservice', 'current_postservice', 'current_work'])
        else:
            return tuple(df.iloc[0][col] for col in ['global_value', 'current_tt', 'current_ist', 'current_preservice', 'current_postservice', 'current_work'])
    return None

# Function to get current labor data.
def get_current_labor(code_id):
    df = load_and_filter_df(code_id, pfs.load_labor)
    if df is not None:
        if is_pyspark_df(df):
            rate_per_minute = df.select('rate_per_minute').first()[0]
        else:
            rate_per_minute = df['rate_per_minute'].iloc[0]
        df = calculate_totals(df, ['nf_', 'f_'], 'rate_per_minute', rate_per_minute)
        return df
    return None

# Function to get current equipment data.
def get_current_equip(code_id):
    df = load_and_filter_df(code_id, pfs.load_equip)
    if df is not None:
        if is_pyspark_df(df):
            df = df.withColumn("time_factor", (F.col('price') / F.col('useful_life')) / F.col('minutes_per_year'))
        else:
            df['time_factor'] = (df['price'] / df['useful_life']) / df['minutes_per_year']
        df = calculate_totals(df, ['nf_time', 'f_time'], 'price', 'time_factor')
        return df
    return None

# Function to get current supply data.
def get_current_supply(code_id):
    df = load_and_filter_df(code_id, pfs.load_supply)
    if df is not None:
        if is_pyspark_df(df):
            df = df.withColumn("total_price", F.col('price'))
        else:
            df['total_price'] = df['price']
        df = calculate_totals(df, ['nf_quantity', 'f_quantity'], 'price', 'total_price')
        return df
    return None

# Remaining functions adapted for both PySpark and Pandas

def get_filtered_rvu(code_id):
    df = load_and_filter_df(code_id, pfs.load_rvu)
    return df

def get_direct_pe(code_id):
    df1 = get_current_supply(code_id)
    df2 = get_current_equip(code_id)
    df3 = get_current_labor(code_id)
    if df1 is not None and df2 is not None and df3 is not None:
        if is_pyspark_df(df1):
            current_dpe_tot_f = df1.select(F.sum('tot_f')).first()[0] + df2.select(F.sum('tot_f')).first()[0] + df3.select(F.sum('tot_f')).first()[0]
            current_dpe_tot_nf = df1.select(F.sum('tot_nf')).first()[0] + df2.select(F.sum('tot_nf')).first()[0] + df3.select(F.sum('tot_nf')).first()[0]
        else:
            current_dpe_tot_f = df1['tot_f'].sum() + df2['tot_f'].sum() + df3['tot_f'].sum()
            current_dpe_tot_nf = df1['tot_nf'].sum() + df2['tot_nf'].sum() + df3['tot_nf'].sum()
        return current_dpe_tot_f, current_dpe_tot_nf
    return None, None

def get_df_global(code_id):
    df = load_and_filter_df(code_id, pfs.load_ruc, 'code_id')
    if df is not None:
        if is_pyspark_df(df):
            search_global_value = df.select('global_value').first()[0]
            return df.filter(F.col('global_value') == search_global_value)
        else:
            search_global_value = df['global_value'].iloc[0]
            return df[df['global_value'] == search_global_value]
    return None

def get_filtered_data(code_id, tt_lower, tt_upper, ist_lower, ist_upper):
    df = get_df_global(code_id)
    if df is not None:
        if is_pyspark_df(df):
            df_filtered = df.filter((F.col('current_tt') >= tt_lower) & (F.col('current_tt') <= tt_upper) & 
                                    (F.col('current_ist') >= ist_lower) & (F.col('current_ist') <= ist_upper))
            work_25th_percentile = df_filtered.approxQuantile('current_work', [0.25], 0.05)[0]
            df_work25th = df_filtered.filter(F.col('current_work') <= work_25th_percentile)
        else:
            df_filtered = df[(df['current_tt'] >= tt_lower) & (df['current_tt'] <= tt_upper) &
                             (df['current_ist'] >= ist_lower) & (df['current_ist'] <= ist_upper)]
            work_25th_percentile = np.percentile(df_filtered['current_work'], 25)
            df_work25th = df_filtered[df_filtered['current_work'] <= work_25th_percentile]
        return df_filtered, df_work25th
    return None, None

def get_search_params(code_id):
    search_global_value, current_tt, current_ist, _, _, _ = get_current_intensity(code_id)
    if search_global_value is not None:
        tt_lower = max(current_tt - 5, 1)
        tt_upper = current_tt + 5
        ist_lower = current_ist
        ist_upper = current_ist
        tt_min = max(current_tt - current_tt, 0)
        tt_max = tt_upper * 2.0
        ist_min = max(current_ist - current_ist, 0)
        ist_max = ist_upper * 2.0
        return tt_min, tt_max, ist_min, ist_max, tt_lower, tt_upper, ist_lower, ist_upper
    return None

def get_time_bounds(code_id):
    _, current_tt, current_ist = get_current_intensity(code_id)
    if current_tt is not None and current_ist is not None:
        tt_min = 0
        tt_max = current_tt * 2.0
        ist_min = 0
        ist_max = current_ist * 2.0
        return tt_min, tt_max, ist_min, ist_max
    return None, None, None, None

def get_tt_ratio(ruc_tt, current_tt):
    return ruc_tt / current_tt if current_tt != 0 else 0.0

def get_tt_ratio_percent(tt_ratio):
    return tt_ratio * 100

def get_tt_ratio_work(tt_ratio, current_work):
    return tt_ratio * current_work

def get_ist_ratio(ruc_ist, current_ist):
    return ruc_ist / current_ist if current_ist != 0 else 0.0

def get_ist_ratio_work(ist_ratio, current_work):
    return ist_ratio * current_work

def filtered_search_count(df_filtered):
    if is_pyspark_df(df_filtered):
        return df_filtered.count()
    else:
        return len(df_filtered)

def quartile_search_count(df_work25th):
    if is_pyspark_df(df_work25th):
        return df_work25th.count()
    else:
        return len(df_work25th)

def get_median_work25th(df_work25th):
    if is_pyspark_df(df_work25th):
        return df_work25th.approxQuantile('current_work', [0.5], 0.05)[0]
    else:
        return df_work25th['current_work'].median()

def count_lower_values(df_work25th):
    ruc_work = st.session_state.get('ruc_work', 0)
    if is_pyspark_df(df_work25th):
        return df_work25th.filter(F.col('current_work') < ruc_work).count()
    else:
        return (df_work25th['current_work'] < ruc_work).sum()

def filter_for_crosswalks(df_work25th, cms_work):
    if is_pyspark_df(df_work25th):
        return df_work25th.filter(F.col('current_work') == cms_work)
    else:
        return df_work25th[df_work25th['current_work'] == cms_work]

def filter_by_hcpcs(df, hcpcs_code):
    if is_pyspark_df(df):
        return df.filter(F.col('hcpcs') == hcpcs_code)
    else:
        return df[df['hcpcs'] == hcpcs_code]
