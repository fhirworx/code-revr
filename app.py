import streamlit as st
from session import SessionManager, FormInputs, AppDisplay

st.set_page_config(layout="wide")

session_manager = SessionManager()
form_inputs = FormInputs()
display = AppDisplay()

# Initialize all session variables
if st.session_state.hcpcs not in st.session_state:
    session_manager.initialize_session_vars()

if st.session_state['stage'] >= 1:
    session_manager.update_session_state_directs()
    session_manager.update_session_state_current_intensity()
    session_manager.update_session_state_time_bounds()

if st.session_state['stage'] > 2:
    session_manager.update_session_state_filtered_data()
    session_manager.update_session_state_refinements()

with st.sidebar:
    form_inputs.display_form()

tab1, tab2, tab3, tab4 = st.tabs(
    ["#1. Direct Practice Expense", "#2. Comparison Codes", "#3. Input Refinements", "#4. Briefing Summary"])

with tab1:
    if st.session_state.hcpcs is not None:
        display.direct_pe_inputs()

with tab2:
    if st.session_state.tt_lower is not None:
        display.filtered_table_results()
        display.potential_crosswalks()

with tab3:
    if st.session_state.current_work is not None:
        display.value_input_sections()

with tab4:
    if st.session_state.cms_work is not None:
        display.charts_and_text()

with st.container():
    st.write("Session State:", st.session_state)
