import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from funcs import DPEICalculator, DirectPECalculator, IntensityCalculator, RefinementFunctions

dpei = DPEICalculator()
directs = DirectPECalculator()
intents = IntensityCalculator()
refine = RefinementFunctions()


class SessionManager:
    def __init__(self):
        self.session_keys = [
            'hcpcs', 'search_global_value', 'current_tt', 'current_ist', 'current_work',
            'current_preservice', 'current_postservice', 'ruc_tt', 'ruc_ist', 'ruc_work',
            'ruc_preservice', 'ruc_postservice', 'cms_tt', 'cms_ist', 'cms_work',
            'cms_preservice', 'cms_postservice', 'tt_upper', 'tt_lower', 'ist_upper',
            'ist_lower', 'tt_min', 'tt_max', 'ist_min', 'ist_max',
            'df_filtered', 'df_work25th', 'df_current_labor', 'df_current_supply',
            'df_current_equipment', 'current_dpe_tot_f', 'current_dpe_tot_nf', 'potential_crosswalks',
            'tt_ratio', 'tt_ratio_percent', 'tt_ratio_work', 'ist_ratio', 'ist_ratio_work',
            'filtered_search_count', 'quartile_search_count', 'median_work25th',
            'count_lower_values', 'stage'
        ]
        self.initialize_session_vars()

    def initialize_session_vars(self):
        """
        Initializes all session variables to None if they are not already set.
        """
        for key in self.session_keys:
            if key not in st.session_state:
                st.session_state[key] = None
        if st.session_state['stage'] is None:
            st.session_state['stage'] = 0

    def update_session_state_directs(self):
            hcpcs = st.session_state['hcpcs']
            df_current_equipment = dpei.get_current_equip(hcpcs=hcpcs)
            df_current_labor = dpei.get_current_labor(hcpcs=hcpcs)
            df_current_supply = dpei.get_current_supply(hcpcs=hcpcs)
            current_dpe_tot_f, current_dpe_tot_nf = directs.get_direct_pe(hcpcs=hcpcs)
            st.session_state['df_current_equipment'] = df_current_equipment
            st.session_state['df_current_labor'] = df_current_labor
            st.session_state['df_current_supply'] = df_current_supply
            st.session_state['current_dpe_tot_f'] = current_dpe_tot_f
            st.session_state['current_dpe_tot_nf'] = current_dpe_tot_nf

    def update_session_state_current_intensity(self):
            hcpcs = st.session_state['hcpcs']
            current = intents.get_current_intensity(hcpcs=hcpcs)
            st.session_state['search_global_value'] = current[0]
            st.session_state['current_tt'] = current[1]
            st.session_state['current_ist'] = current[2]
            st.session_state['current_preservice'] = current[3]
            st.session_state['current_postservice'] = current[4]
            st.session_state['current_work'] = current[5]

    def update_session_state_time_bounds(self):
            hcpcs = st.session_state['hcpcs']
            time_bounds = intents.get_time_bounds(hcpcs=hcpcs)
            st.session_state['tt_min'] = time_bounds[0]
            st.session_state['tt_max'] = time_bounds[1]
            st.session_state['ist_min'] = time_bounds[2]
            st.session_state['ist_max'] = time_bounds[3]

    def update_session_state_filtered_data(self):
            hcpcs = st.session_state['hcpcs']
            search_global_value = st.session_state['search_global_value']
            tt_lower = st.session_state['tt_lower']
            tt_upper = st.session_state['tt_upper']
            ist_lower = st.session_state['ist_lower']
            ist_upper = st.session_state['ist_upper']
            filtered_data = intents.get_filtered_data(search_global_value=search_global_value, tt_lower=tt_lower, tt_upper=tt_upper, ist_lower=ist_lower, ist_upper=ist_upper)
            st.session_state['df_filtered'] = filtered_data[0]
            st.session_state['df_work25th'] = filtered_data[1]
    def update_session_state_refinements(self):
            current_tt = st.session_state['current_tt']
            current_ist = st.session_state['current_ist']
            current_work = st.session_state['current_work']
            ruc_tt = st.session_state['ruc_tt']
            ruc_ist = st.session_state['ruc_ist']
            ruc_work = st.session_state['ruc_work']
            cms_work = st.session_state['cms_work']
            df_filtered = st.session_state['df_filtered']
            df_work25th = st.session_state['df_work25th']
            tt_ratio = refine.get_tt_ratio(ruc_tt=ruc_tt, current_tt=current_tt)
            tt_ratio_percent = refine.get_tt_ratio_percent(tt_ratio=tt_ratio)
            tt_ratio_work = refine.get_tt_ratio_work(tt_ratio=tt_ratio, current_work=current_work)
            ist_ratio = refine.get_ist_ratio(ruc_ist=ruc_ist, current_ist=current_ist)
            ist_ratio_work = refine.get_ist_ratio_work(ist_ratio=ist_ratio, current_work=current_work)
            filtered_search_count = refine.filtered_search_count(df_filtered=df_filtered)
            quartile_search_count = refine.quartile_search_count(df_work25th=df_work25th)
            median_work25th = refine.get_median_work25th(df_work25th=df_work25th)
            count_lower_values = refine.count_lower_values(df_work25th=df_work25th, ruc_work=ruc_work)
            potential_crosswalks = refine.filter_for_crosswalks(df_work25th=df_work25th, cms_work=cms_work)
            st.session_state['tt_ratio'] = tt_ratio
            st.session_state['tt_ratio_percent'] = tt_ratio_percent
            st.session_state['tt_ratio_work'] = tt_ratio_work
            st.session_state['ist_ratio'] = ist_ratio
            st.session_state['ist_ratio_work'] = ist_ratio_work
            st.session_state['filtered_search_count'] = filtered_search_count
            st.session_state['quartile_search_count'] = quartile_search_count
            st.session_state['median_work25th'] = median_work25th
            st.session_state['count_lower_values'] = count_lower_values
            st.session_state['potential_crosswalks'] = potential_crosswalks
class FormInputs:
    def set_state(self, i):
        st.session_state.stage = i

    def display_form(self):
        if st.session_state.stage >= 0:
            self.initial_hcpcs()
        if st.session_state.stage >= 1:
            self.ist_range()
            self.tt_range()
            self.refine_search()

    def initial_hcpcs(self):
        st.text_input(
            label='Enter a Valid HCPCS Code',
            key='hcpcs',
            on_change=self.set_state,
            args=[1]
        )

    def ist_range(self):
        st.slider(
            label="Select the intraservice time range for comparison codes in the search:",
            value=(st.session_state.current_ist, st.session_state.current_ist),
            step=1.0,
            min_value=st.session_state.ist_min,
            max_value=st.session_state.ist_max,
            key='ist_range',
            on_change=self.set_state,
            args=[2]
        )
        st.session_state.ist_lower = st.session_state.ist_range[0]
        st.session_state.ist_upper = st.session_state.ist_range[1]

    def tt_range(self):
        st.slider(
            label="Select the total time range for comparison codes in the search:",
            value=(st.session_state.current_tt, st.session_state.current_tt),
            step=1.0,
            min_value=st.session_state.tt_min,
            max_value=st.session_state.tt_max,
            key='tt_range',
            on_change=self.set_state,
            args=[2]
        )
        st.session_state.tt_lower = st.session_state.tt_range[0]
        st.session_state.tt_upper = st.session_state.tt_range[1]

    def refine_search(self):
        refine_time = st.button(
            label="Refine Time",
            on_click=self.set_state,
            args=[3]
        )

    def reset_search(self):
        reset_search = st.button(
            label="Reset",
            on_click=self.set_state,
            args=[0]
        )

    def current_values(self):
        st.number_input('Current Total Time', value=st.session_state.current_tt, key='current_tt', disabled=True)
        st.number_input('Current Intraservice Time', value=st.session_state.current_ist, key='current_ist', disabled=True)
        st.number_input('Current Work', value=st.session_state.current_work, key='current_work', disabled=True)
        st.number_input('Current Preservice', value=st.session_state.current_preservice, key='current_preservice', disabled=True)
        st.number_input('Current Postservice', value=st.session_state.current_postservice, key='current_postservice', disabled=True)

    def ruc_values(self):
        st.number_input('RUC Total Time', value=st.session_state.current_tt, key='ruc_tt')
        st.number_input('RUC Intraservice Time', value=st.session_state.current_ist, key='ruc_ist')
        st.number_input('RUC Work', value=st.session_state.current_work, key='ruc_work')
        st.number_input('RUC Preservice', value=st.session_state.current_preservice, key='ruc_preservice')
        st.number_input('RUC Postservice', value=st.session_state.current_postservice, key='ruc_postservice')

    def cms_values(self):
        st.number_input('CMS Total Time', value=st.session_state.current_tt, key='cms_tt')
        st.number_input('CMS Intraservice Time', value=st.session_state.current_ist, key='cms_ist')
        st.number_input('CMS Work', value=st.session_state.current_work, key='cms_work')
        st.number_input('CMS Preservice', value=st.session_state.current_preservice, key='cms_preservice')
        st.number_input('CMS Postservice', value=st.session_state.current_postservice, key='cms_postservice')


class AppDisplay:
    @staticmethod
    def search_results():
        st.write(f"# Search Results for {st.session_state.hcpcs}")

    @staticmethod
    def direct_pe_inputs():
        st.subheader("Direct PE Inputs")
        st.write("Supplies")
        st.dataframe(st.session_state.df_current_supply)
        st.write("Equipment")
        st.dataframe(st.session_state.df_current_equipment)
        st.write("Labor")
        st.dataframe(st.session_state.df_current_labor)
        st.write(f"Total direct PE for facility setting: {st.session_state.current_dpe_tot_f} ")
        st.write(f"Total direct PE for non-facility setting: {st.session_state.current_dpe_tot_nf}")

    @staticmethod
    def filtered_table_results():
        st.subheader("Filtered Search Results")
        st.dataframe(st.session_state.df_filtered)
        st.subheader("Work 25th Percentile Options")
        st.dataframe(st.session_state.df_work25th)

    def value_input_sections(self):
        if st.session_state.current_work is not None:
            col1, col2, col3 = st.columns([3, 3, 3])
            self.current_values(col1)
            self.ruc_values(col2)
            self.cms_values(col3)

    def current_values(self, column):
        with column:
            st.subheader(f"Current Values for {st.session_state.hcpcs}")
            FormInputs.current_values(self)

    def ruc_values(self, column):
        with column:
            st.subheader(f"RUC Values for {st.session_state.hcpcs}")
            FormInputs.ruc_values(self)

    def cms_values(self, column):
        with column:
            st.subheader(f"CMS Values for {st.session_state.hcpcs}")
            FormInputs.cms_values(self)

    @staticmethod
    def potential_crosswalks():
        with st.container():
            st.subheader(f"Potential Crosswalk Codes with Work RVU: {st.session_state.cms_work}")
            if st.session_state.potential_crosswalks is not None:
                df = st.session_state.potential_crosswalks
                st.dataframe(df)
            else:
                st.write(
                    f'No potential crosswalks found for {st.session_state.hcpcs} with CMS work value of {st.session_state.cms_work}')

    def charts_and_text(self):
        """
        Displays charts and briefing text.
        """
        self.charts()
        self.briefing_text()

    def create_charts(self):
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
            name='Current'
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
            'group': ['Current'] * 5 + ['RUC'] * 5 + ['CMS'] * 5
        })
        fig_bar = px.bar(df, x='category', y='value', color='group', barmode='group')
        return fig_radar, fig_bar

    def charts(self):
        fig_radar, fig_bar = self.create_charts()
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_radar)
        with col2:
            st.plotly_chart(fig_bar)

    def briefing_text(self):
        st.write(
            f"The code review search is for {st.session_state.hcpcs}. The RUC recommended a work RVU of {st.session_state.ruc_work} and Total Time of {st.session_state.ruc_tt}. The Total Time search parameters for this review are from {st.session_state.tt_lower} to {st.session_state.tt_upper} minutes. The intraservice time search parameters are from {st.session_state.ist_lower} to {st.session_state.ist_upper} minutes. The Median Work RVU for the search is {st.session_state.median_work25th}. The count of all reference codes in the search is {st.session_state.filtered_search_count}. Of these, the count of codes in the bottom quartile, based on work RVU, is {st.session_state.quartile_search_count}. The initial search identified {st.session_state.filtered_search_count} codes with a global value of {st.session_state.search_global_value} and with a total time from {st.session_state.tt_lower} to {st.session_state.tt_upper}. Of the codes reviewed, {st.session_state.count_lower_values} of the {st.session_state.count_lower_values} codes in the bottom quartile of the reference services found in the RUC dB search have wRVUs lower than the RUC-recommended wRVU of {st.session_state.ruc_work}. The total time ratio between the current time of {st.session_state.current_tt} minutes and the recommended time established by the RUC of {st.session_state.ruc_tt} minutes is {st.session_state.tt_ratio}. This ratio equals {st.session_state.tt_ratio_percent} percent, and when multiplied by the current wRVU of {st.session_state.current_work} equals {st.session_state.tt_ratio_work}.")
