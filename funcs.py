import pfs_data as pfs
import streamlit as st
import numpy as np

# Helper function to validate a given code ID.
def get_valid_code_id(code_id, df_column='code_id'):
    """
    Validates the given code ID against the data loaded from RUC.
    """
    df = pfs.load_ruc()
    return code_id if code_id in df[df_column].values else None

# Helper function to load data and filter by code ID.
def load_and_filter_df(code_id, load_function, column='hcpcs'):
    """
    Loads a dataframe using the specified load function and filters it by the given code ID.
    """
    code_id = get_valid_code_id(code_id, df_column=column)
    if code_id:
        df = load_function()
        return df[df[column] == code_id]
    return None

# Helper function to calculate total values.
def calculate_totals(df, time_columns, price_column, time_factor):
    """
    Calculates total values for specified time columns in the dataframe.
    """
    for time_column in time_columns:
        df[f'tot_{time_column}'] = df[time_column] * time_factor
    return df

# Function to get current intensity values.
def get_current_intensity(code_id):
    """
    Retrieves current intensity values for the given code ID.
    """
    df = load_and_filter_df(code_id, pfs.load_ruc, 'code_id')
    if df is not None:
        return tuple(df.iloc[0][col] for col in ['global_value', 'current_tt', 'current_ist', 'current_preservice', 'current_postservice', 'current_work'])
    return None

# Function to get current labor data.
def get_current_labor(code_id):
    """
    Retrieves current labor data for the given code ID.
    """
    df = load_and_filter_df(code_id, pfs.load_labor)
    if df is not None:
        rate_per_minute = df['rate_per_minute']
        df = calculate_totals(df, ['nf_', 'f_'], 'rate_per_minute', rate_per_minute)
        return df
    return None

# Function to get current equipment data.
def get_current_equip(code_id):
    """
    Retrieves current equipment data for the given code ID.
    """
    df = load_and_filter_df(code_id, pfs.load_equip)
    if df is not None:
        time_factor = (df['price'] / df['useful_life']) / df['minutes_per_year']
        df = calculate_totals(df, ['nf_time', 'f_time'], 'price', time_factor)
        return df
    return None

# Function to get current supply data.
def get_current_supply(code_id):
    """
    Retrieves current supply data for the given code ID.
    """
    df = load_and_filter_df(code_id, pfs.load_supply)
    if df is not None:
        df = calculate_totals(df, ['nf_quantity', 'f_quantity'], 'price', df['price'])
        return df
    return None

def get_filtered_rvu(code_id):
    """ Retrieves RVU data for a given code ID. """
    df = load_and_filter_df(code_id, pfs.load_rvu)
    return df

def get_direct_pe(code_id):
    """ Calculates the direct practice expense for a given code ID. """
    df1 = get_current_supply(code_id)
    df2 = get_current_equip(code_id)
    df3 = get_current_labor(code_id)
    if df1 is not None and df2 is not None and df3 is not None:
        current_dpe_tot_f = df1['tot_f'].sum() + df2['tot_f'].sum() + df3['tot_f'].sum()
        current_dpe_tot_nf = df1['tot_nf'].sum() + df2['tot_nf'].sum() + df3['tot_nf'].sum()
        return current_dpe_tot_f, current_dpe_tot_nf
    return None, None

def get_df_global(code_id):
    """ Retrieves global data for a given code ID. """
    df = load_and_filter_df(code_id, pfs.load_ruc, 'code_id')
    if df is not None:
        search_global_value = df['global_value'].iloc[0]
        return df[df['global_value'] == search_global_value]
    return None

def get_filtered_data(code_id, tt_lower, tt_upper, ist_lower, ist_upper):
    """ Retrieves filtered data based on time and intensity bounds. """
    df = get_df_global(code_id)
    if df is not None:
        df_filtered = df[(df['current_tt'] >= tt_lower) & (df['current_tt'] <= tt_upper) &
                         (df['current_ist'] >= ist_lower) & (df['current_ist'] <= ist_upper)]
        work_25th_percentile = np.percentile(df_filtered['current_work'], 25)
        df_work25th = df_filtered[df_filtered['current_work'] <= work_25th_percentile]
        return df_filtered, df_work25th
    return None, None

def get_search_params(code_id):
    """ Retrieves search parameters for a given code ID. """
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
    """
    Calculates time bounds based on current intensity values.
    """
    _, current_tt, current_ist = get_current_intensity(code_id)
    if current_tt is not None and current_ist is not None:
        tt_min = 0
        tt_max = current_tt * 2.0
        ist_min = 0
        ist_max = current_ist * 2.0
        return tt_min, tt_max, ist_min, ist_max
    return None, None, None, None

def get_tt_ratio(ruc_tt, current_tt):
    """
    Calculates the time ratio.
    """
    return ruc_tt / current_tt if current_tt != 0 else 0.0

def get_tt_ratio_percent(tt_ratio):
    """
    Converts the time ratio to a percentage.
    """
    return tt_ratio * 100

def get_tt_ratio_work(tt_ratio, current_work):
    """
    Calculates work time based on the time ratio.
    """
    return tt_ratio * current_work

def get_ist_ratio(ruc_ist, current_ist):
    """
    Calculates the intensity ratio.
    """
    return ruc_ist / current_ist if current_ist != 0 else 0.0

def get_ist_ratio_work(ist_ratio, current_work):
    """
    Calculates work intensity based on the intensity ratio.
    """
    return ist_ratio * current_work

def filtered_search_count(df_filtered):
    """
    Counts the number of entries in the filtered DataFrame.
    """
    return len(df_filtered)

def quartile_search_count(df_work25th):
    """
    Counts the number of entries in the 25th percentile DataFrame.
    """
    return len(df_work25th)

def get_median_work25th(df_work25th):
    """
    Calculates the median work value for the 25th percentile DataFrame.
    """
    return df_work25th['current_work'].median()

def count_lower_values(df_work25th):
    """
    Counts the number of values lower than the ruc_work in the DataFrame.
    """
    ruc_work = st.session_state.get('ruc_work', 0)
    return (df_work25th['current_work'] < ruc_work).sum()

def filter_for_crosswalks(df_work25th, cms_work):
    """
    Filters the DataFrame for entries matching the cms_work value.
    """
    return df_work25th[df_work25th['current_work'] == cms_work]

def filter_by_hcpcs(df, hcpcs_code):
    """
    Filters the DataFrame by the HCPCS code.
    """
    return df[df['hcpcs'] == hcpcs_code]