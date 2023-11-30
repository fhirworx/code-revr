import streamlit as st
import funcs as f
import session as s
import display as d

st.set_page_config(layout="wide")

# Initialize all session variables
s.all_session_vars()

# Code ID input section
if st.session_state.code_id is None:
    with st.container():
        st.session_state.code_id = st.text_input("Enter a code ID", value="")

# Main review section
if st.session_state.code_id is not None:
    with st.container():
        st.header(f"Code Review for {st.session_state.code_id}")
        
        # Update and display current lookups
        s.current_lookups()
        s.search_params()
        s.initial_search_lookups()
        s.review_crosswalks()
        s.review_initial_results()

        # Refine search options
        st.subheader("Refine Search")
        s.set_refined_search_params()

        # Display search results
        d.display_search_results()

        # Display direct PE inputs
        d.display_direct_pe_inputs()

        # Input section for current, RUC, and CMS values
        d.display_value_input_sections()

        # Display potential crosswalk codes
        d.display_potential_crosswalks()

        # Display charts and briefing text
        d.display_charts_and_text()

# Footer section with session state debugging (if needed)
with st.container():
    st.write("Session State:", st.session_state)