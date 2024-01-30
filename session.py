import funcs as f
import streamlit as st

def initialize_session_vars():
    """
    Initializes all session variables to None if they are not already set.
    """
    session_keys = [
        'code_id', 'search_global_value', 'current_tt', 'current_ist', 'current_work',
        'current_preservice', 'current_postservice', 'ruc_tt', 'ruc_ist', 'ruc_work',
        'ruc_preservice', 'ruc_postservice', 'cms_tt', 'cms_ist', 'cms_work',
        'cms_preservice', 'cms_postservice', 'tt_upper', 'tt_lower', 'ist_upper',
        'ist_lower', 'tt_min', 'tt_max', 'ist_min', 'ist_max', 'df_global',
        'df_filtered', 'df_work25th', 'df_current_labor', 'df_current_supply',
        'df_current_equipment', 'current_dpe_tot_f', 'current_dpe_tot_nf', 'potential_crosswalks',
        'tt_ratio', 'tt_ratio_percent', 'tt_ratio_work', 'ist_ratio', 'ist_ratio_work',
        'filtered_search_count', 'quartile_search_count', 'median_work25th',
        'count_lower_values'
    ]
    for key in session_keys:
        if key not in st.session_state:
            st.session_state[key] = None

def set_session_values(func, keys):
    """
    Sets the session state values based on the return values of a given function.
    """
    values = func(st.session_state['code_id'])
    for key, value in zip(keys, values):
        st.session_state[key] = value

def set_values_from_function(func, *args):
    """
    Sets the session state values based on the return values of a function
    and the corresponding argument keys.
    """
    values = func(*args)
    if not isinstance(values, tuple):
        values = (values,)
    for i, key in enumerate(args):
        st.session_state[key] = values[i] if i < len(values) else None

def code_id():
    """
    Updates session variables related to code ID.
    """
    keys = ['code_id']
    set_session_values(f.get_code_id, keys)

def current_lookups():
    """
    Updates session variables related to current lookups.
    """
    keys = [
        'df_current_equipment', 'df_current_labor', 'df_current_supply', 'df_global', 'df_filtered', 
        'df_work25th', 'current_dpe_tot_f', 'current_dpe_tot_nf', 'search_global_value', 'current_tt', 
        'current_ist', 'current_preservice', 'current_postservice', 'current_work', 'tt_min', 'tt_max', 
        'ist_min', 'ist_max', 'tt_lower', 'tt_upper', 'ist_lower', 'ist_upper'
    ]
    set_session_values(f.get_current_lookups, keys)

def search_parameters():
    """
    Updates session variables related to search parameters.
    """
    keys = ['tt_min', 'tt_max', 'ist_min', 'ist_max', 'tt_lower', 'tt_upper', 'ist_lower', 'ist_upper']
    set_session_values(f.get_search_parameters, keys)

def initial_search_lookups():
    """
    Updates session variables for initial search lookups.
    """
    keys = ['df_filtered', 'df_work25th']
    set_session_values(f.get_filtered_data, keys)

def review_default_values():
    if st.session_state.current_tt is not None:
        keys = [
            'cms_tt', 'cms_ist', 'cms_work', 'cms_preservice', 'cms_postservice',
            'ruc_tt', 'ruc_ist', 'ruc_work', 'ruc_preservice', 'ruc_postservice'
        ]
        set_session_values(f.default_review_values, keys)

def review_initial_results():
    """
    Updates session variables for reviewing initial results.
    """
    keys = [
        'filtered_search_count', 'tt_ratio', 'ist_ratio', 'tt_ratio_percent', 'tt_ratio_work', 'ist_ratio_work', 
        'quartile_search_count', 'median_work25th', 'count_lower_values', 'potential_crosswalks'
    ]
    set_session_values(f.get_review_initial_results, keys)
