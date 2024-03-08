import pandas as pd
import streamlit as st

@st.cache_data
def load_ruc(filepath='./raw_data/raw.csv'):
    df = pd.read_csv(filepath)
    column_mapping = {
        'CPT Code': 'hcpcs',
        'Long Desc': 'long_desc',
        'Global': 'global_value',
        'Work RVU': 'current_work',
        'Non-Facility Total RVU': 'nf_rvu',
        'Facility Total RVU': 'f_rvu',
        'Pre Time Package': 'pre_time_pckg',
        'Pre Eval Time': 'pre_eval_time',
        'Pre Positioning Time': 'pre_posi_time',
        'Pre Scrub, Dress, Wait Time': 'pre_sdw_time',
        'Intra Time': 'current_ist',
        'Immediate Post Time': 'post_imed_time',
        'Post-op Visit Time': 'post_visit_time',
        'Total Time': 'current_tt',
        'Hospital Post-op Visit Count': 'hosp_postop_visit_count',
        'Office Post-op Visit Count': 'off_postop_visit_count',
        'Time Source': 'time_source',
        'Most Recent RUC Review': 'last_ruc_review',
        'Top_Specialty': 'top_specialty',
        'IWPUT': 'current_iwput',
        'MPC': 'mpc',
        'Vignette': 'vignette',
        '2021 Medicare Utilization': 'medicare21util',
        '2021 Medicare Allowed Charges': 'medicare21allowed'
    }
    df = df.rename(columns=column_mapping)
    df = pd.read_csv(filepath, dtype={column: 'str' for column in ['CPT Code', 'Global']})
    df.rename(columns=column_mapping, inplace=True)
    columns_to_clean = ['pre_time_pckg', 'pre_posi_time', 'pre_eval_time', 'pre_sdw_time',
                        'post_imed_time', 'post_visit_time', 'current_work', 'current_tt',
                        'current_ist', 'hosp_postop_visit_count', 'off_postop_visit_count']
    df[columns_to_clean] = df[columns_to_clean].apply(pd.to_numeric, errors='coerce').fillna(0)
    df['current_preservice'] = df[['pre_time_pckg', 'pre_eval_time', 'pre_posi_time']].sum(axis=1).fillna(0)
    df['current_postservice'] = df[['post_imed_time', 'post_visit_time']].sum(axis=1).fillna(0)
    df = df[df['current_work'] > 0]
    return df

@st.cache_data
def load_supply():
    filepath = './raw_data/supply.xlsx'  # Updated for Excel file
    df = pd.read_excel(filepath)
    return df

@st.cache_data
def load_equip():
    filepath = './raw_data/equip.xlsx'
    df = pd.read_excel(filepath)
    return df

@st.cache_data
def load_labor():
    filepath = './raw_data/labor.xlsx'
    df = pd.read_excel(filepath)
    return df

@st.cache_data
def load_rvu(filepath='./raw_data/rvu.csv'):
    df = pd.read_csv(filepath, skiprows=12)
    new_column_names = [
        'hcpcs', 'mod', 'description', 'status_code', 'not_used_for_medicare_payment',
        'work_rvu', 'nf_pe_rvu', 'nf_indicator', 'f_pe_rvu', 'f_indicator',
        'mp_rvu', 'nf_total', 'f_total', 'pctc_ind', 'glob_days', 'pre_op',
        'intra_op', 'post_op', 'mult_proc', 'bilat_surg', 'asst_surg', 'co_surg', 'team_surg',
        'endo_base', 'conv_factor', 'phys_sup_diag', 'calc_flag', 'diag_img_ind', 'pe_opps_nf', 'pe_opps_f',
        'mp_opps'
    ]
    df.columns = new_column_names
    columns_to_convert = ['hcpcs', 'mod', 'endo_base']
    for column in columns_to_convert:
        df[column] = df[column].astype(str)
    return df
