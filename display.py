import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def display_search_results():
    st.write(f"# Search Results for {st.session_state.code_id}")

def display_direct_pe_inputs():
    """
    Displays the Direct PE inputs for the given code ID.
    """
    st.subheader("Direct PE Inputs")
    st.write("Supplies")
    st.dataframe(st.session_state.df_current_supply)
    st.write("Equipment")
    st.dataframe(st.session_state.df_current_equipment)
    st.write("Labor")
    st.dataframe(st.session_state.df_current_labor)
    st.write(f"Total direct PE for facility setting: {st.session_state.current_dpe_tot_f} Total direct PE for non-facility setting: {st.session_state.current_dpe_tot_nf}")

def display_value_input_sections():
    """
    Displays input sections for current, RUC, and CMS values.
    """
    if st.session_state.cms_work is not None:
        col1, col2, col3 = st.columns([3, 3, 3])
        display_current_values(col1)
        display_ruc_values(col2)
        display_cms_values(col3)

def display_current_values(column):
    """
    Displays input fields for current values.
    """
    with column:
        st.subheader(f"Current Values for {st.session_state.code_id}")
        st.session_state.current_tt = st.number_input(label='Current Total Time', value=st.session_state.current_tt, disabled=True)
        st.session_state.current_ist = st.number_input(label='Current Intraservice Time', value=st.session_state.current_ist, disabled=True)
        st.session_state.current_work = st.number_input(label='Current Work', value=st.session_state.current_work, disabled=True)
        st.session_state.currnet_preservice = st.number_input(label='Current Preservice', value=st.session_state.current_preservice, disabled=True)
        st.session_state.current_postservice = st.number_input(label='Current Postservice', value=st.session_state.current_postservice, disabled=True)

def display_ruc_values(column):
    """
    Displays input fields for RUC values.
    """
    with column:
        st.subheader(f"RUC Values for {st.session_state.code_id}")
        st.session_state.ruc_tt = st.number_input(label='RUC Total Time', value=st.session_state.ruc_tt, placeholder=st.session_state.current_tt)
        st.session_state.ruc_ist = st.number_input(label='RUC Intraservice Time', value=st.session_state.ruc_ist, placeholder=st.session_state.current_ist)
        st.session_state.ruc_work = st.number_input(label='RUC Work', value=st.session_state.ruc_work, placeholder=st.session_state.current_work)
        st.session_state.ruc_preservice = st.number_input(label='RUC Preservice', value=st.session_state.ruc_preservice, placeholder=st.session_state.current_preservice)
        st.session_state.ruc_postservice = st.number_input(label='RUC Postservice', value=st.session_state.ruc_postservice, placeholder=st.session_state.current_postservice)

def display_cms_values(column):
    """
    Displays input fields for CMS values.
    """
    with column:
        st.subheader(f"CMS Values for {st.session_state.code_id}")
        st.session_state.cms_tt = st.number_input(label='CMS Total Time', value=st.session_state.cms_tt, placeholder=st.session_state.ruc_tt)
        st.session_state.cms_ist = st.number_input(label='CMS Intraservice Time', value=st.session_state.cms_ist, placeholder=st.session_state.ruc_ist)
        st.session_state.cms_work = st.number_input(label='CMS Work', value=st.session_state.cms_work, placeholder=st.session_state.ruc_work)
        st.session_state.cms_preservice = st.number_input(label='CMS Preservice', value=st.session_state.cms_preservice, placeholder=st.session_state.ruc_preservice)
        st.session_state.cms_postservice = st.number_input(label='CMS Postservice', value=st.session_state.cms_postservice, placeholder=st.session_state.ruc_postservice)

# Display potential crosswalk codes
def display_potential_crosswalks():
    with st.container():
        st.subheader(f"Potential Crosswalk Codes with Work RVU: {st.session_state.cms_work}")
        df = st.session_state.potential_crosswalks
        st.dataframe(df)
        if df.empty:
            st.write(f'No potential crosswalks found for {st.session_state.code_id} with CMS work value of {st.session_state.cms_work}')
        else:
            st.dataframe(st.session_state.potential_crosswalks)

# Display charts and briefing text
def display_charts_and_text():
    """
    Displays charts and briefing text.
    """
    display_charts()
    display_briefing_text()

def create_charts():
    values = [
        st.session_state.current_tt,
        st.session_state.current_ist,
        st.session_state.current_work,
        st.session_state.current_preservice,
        st.session_state.current_postservice,
        st.session_state.ruc_tt,
        st.session_state.ruc_ist,
        st.session_state.ruc_work,
        st.session_state.ruc_preservice,
        st.session_state.ruc_postservice,
        st.session_state.cms_tt,
        st.session_state.cms_ist,
        st.session_state.cms_work,
        st.session_state.cms_preservice,
        st.session_state.cms_postservice
    ]
    max_value = max(values)
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values[0:5],
        theta=['tt', 'ist', 'work', 'preservice', 'postservice'],
        fill='toself',
        name='current'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=values[5:10],
        theta=['tt', 'ist', 'work', 'preservice', 'postservice'],
        fill='toself',
        name='RUC'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=values[10:15],
        theta=['tt', 'ist', 'work', 'preservice', 'postservice'],
        fill='toself',
        name='CMS'
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_value]  
            )),
        showlegend=True
    )
    df = pd.DataFrame({
        'category': ['tt', 'ist', 'work', 'preservice', 'postservice'] * 3,
        'value': values,
        'group': ['current'] * 5 + ['RUC'] * 5 + ['CMS'] * 5
    })
    fig_bar = px.bar(df, x='category', y='value', color='group', barmode='group')
    return fig_radar, fig_bar

def display_charts():
    fig_radar, fig_bar = create_charts()
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_radar)
    with col2:
        st.plotly_chart(fig_bar)

def display_briefing_text():
    st.write(f"The code review search is for {st.session_state.code_id}. The RUC recommended a work RVU of {st.session_state.ruc_work} and Total Time of {st.session_state.ruc_tt}. The Total Time search parameters for this review are from {st.session_state.tt_lower} to {st.session_state.tt_upper} minutes. The intraservice time search parameters are from {st.session_state.ist_lower} to {st.session_state.ist_upper} minutes. The Median Work RVU for the search is {st.session_state.median_work25th}. The count of all reference codes in the search is {st.session_state.filtered_search_count}. Of these, the count of codes in the bottom quartile, based on work RVU, is {st.session_state.quartile_search_count}. The initial search identified {st.session_state.filtered_search_count} codes with a global value of {st.session_state.search_global_value} and with a total time from {st.session_state.tt_lower} to {st.session_state.tt_upper}. Of the codes reviewed, {st.session_state.count_lower_values} of the {st.session_state.count_lower_values} codes in the bottom quartile of the reference services found in the RUC dB search have wRVUs lower than the RUC-recommended wRVU of {st.session_state.ruc_work}. The total time ratio between the current time of {st.session_state.current_tt} minutes and the recommended time established by the RUC of {st.session_state.ruc_tt} minutes is {st.session_state.tt_ratio}. This ratio equals {st.session_state.tt_ratio_percent} percent, and when multiplied by the current wRVU of {st.session_state.current_work} equals {st.session_state.tt_ratio_work}.")