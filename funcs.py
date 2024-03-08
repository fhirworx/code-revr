import pfs_data as pfs
import pandas as pd
import numpy as np


class DataLoader:
    @staticmethod
    def load_and_filter_df(hcpcs, load_function):
        df = load_function()
        if not df.empty and 'hcpcs' in df.columns:
            filtered_df = df[df['hcpcs'] == hcpcs]
            return filtered_df
        else:
            return pd.DataFrame()


class DPEICalculator:
    @staticmethod
    def get_current_labor(hcpcs):
        df = DataLoader.load_and_filter_df(hcpcs, pfs.load_labor)
        if not df.empty:
            nf_columns = [col for col in df.columns if col.startswith('nf')]
            f_columns = [col for col in df.columns if col.startswith('f')]
            df['nf_total'] = df[nf_columns].sum(axis=1) * df['rate_per_minute']
            df['f_total'] = df[f_columns].sum(axis=1) * df['rate_per_minute']
            return df
        return pd.DataFrame()

    @staticmethod
    def get_current_supply(hcpcs):
        df = DataLoader.load_and_filter_df(hcpcs, pfs.load_supply)
        if not df.empty:
            df['nf_total'] = df['nf_quantity'] * df['price']
            df['f_total'] = df['f_quantity'] * df['price']
            return df
        return pd.DataFrame()

    @staticmethod
    def get_current_equip(hcpcs):
        df = DataLoader.load_and_filter_df(hcpcs, pfs.load_equip)
        if not df.empty:
            df['nf_total'] = (((df['price'] / df['useful_life']) / df['minutes_per_year']) * df['nf_time']).fillna(0)
            df['f_total'] = (((df['price'] / df['useful_life']) / df['minutes_per_year']) * df['f_time']).fillna(0)
            return df
        return pd.DataFrame()


class DirectPECalculator:
    @staticmethod
    def get_direct_pe(hcpcs):
        df1 = DPEICalculator.get_current_supply(hcpcs)
        df2 = DPEICalculator.get_current_equip(hcpcs)
        df3 = DPEICalculator.get_current_labor(hcpcs)
        if not df1.empty and not df2.empty and not df3.empty:
            current_dpe_tot_f = df1['f_total'].sum() + df2['f_total'].sum() + df3['f_total'].sum()
            current_dpe_tot_nf = df1['nf_total'].sum() + df2['nf_total'].sum() + df3['nf_total'].sum()
            return current_dpe_tot_f, current_dpe_tot_nf
        return 0, 0


class IntensityCalculator:
    @staticmethod
    def get_current_intensity(hcpcs):
        df = DataLoader.load_and_filter_df(hcpcs, pfs.load_ruc)
        if not df.empty:
            return tuple(df.iloc[0][col] for col in
                         ['global_value', 'current_tt', 'current_ist', 'current_preservice', 'current_postservice',
                          'current_work'])
        return None

    @staticmethod
    def get_time_bounds(hcpcs):
        """
        Calculates time bounds based on current intensity values.
        """
        _, current_tt, current_ist, _, _, _ = IntensityCalculator.get_current_intensity(hcpcs)
        if current_tt is not None and current_ist is not None:
            tt_min = 0.0
            tt_max = current_tt * 2.0
            ist_min = 0.0
            ist_max = current_ist * 2.0
            return tt_min, tt_max, ist_min, ist_max
        return None, None, None, None

    @staticmethod
    def get_filtered_data(search_global_value, tt_lower, tt_upper, ist_lower, ist_upper):
        df = pfs.load_ruc()
        if not df.empty:
            condition = (df['global_value'] == search_global_value) & (df['current_tt'] >= tt_lower) & (
                        df['current_tt'] <= tt_upper) & (df['current_ist'] >= ist_lower) & (
                                    df['current_ist'] <= ist_upper)
            df_filtered = df[condition].dropna(subset=['current_work'])
            work_25th_percentile = np.percentile(df_filtered['current_work'], 25)
            df_work25th = df_filtered[df_filtered['current_work'] <= work_25th_percentile]
            return df_filtered, df_work25th
        return pd.DataFrame(), pd.DataFrame()


class RefinementFunctions:
    @staticmethod
    def get_tt_ratio(ruc_tt, current_tt):
        """
        Calculates the time ratio.
        """
        return ruc_tt / current_tt if current_tt != 0 else 0.0

    @staticmethod
    def get_tt_ratio_percent(tt_ratio):
        """
        Converts the time ratio to a percentage.
        """
        return tt_ratio * 100

    @staticmethod
    def get_tt_ratio_work(tt_ratio, current_work):
        """
        Calculates work time based on the time ratio.
        """
        return tt_ratio * current_work

    @staticmethod
    def get_ist_ratio(ruc_ist, current_ist):
        """
        Calculates the intensity ratio.
        """
        return ruc_ist / current_ist if current_ist != 0 else 0.0

    @staticmethod
    def get_ist_ratio_work(ist_ratio, current_work):
        """
        Calculates work intensity based on the intensity ratio.
        """
        return ist_ratio * current_work

    @staticmethod
    def filtered_search_count(df_filtered):
        """
        Counts the number of entries in the filtered DataFrame.
        """
        return len(df_filtered)

    @staticmethod
    def quartile_search_count(df_work25th):
        """
        Counts the number of entries in the 25th percentile DataFrame.
        """
        return len(df_work25th)

    @staticmethod
    def get_median_work25th(df_work25th):
        """
       Calculates the median work value for the 25th percentile DataFrame.
       """
        return df_work25th['current_work'].median()

    @staticmethod
    def count_lower_values(df_work25th, ruc_work):
        """
       Counts the number of values lower than the ruc_work in the DataFrame.
       """
        return (df_work25th['current_work'] < ruc_work).sum()

    @staticmethod
    def filter_for_crosswalks(df_work25th, cms_work):
        """
       Filters the DataFrame for entries matching the cms_work value.
       """
        return df_work25th[df_work25th['current_work'] == cms_work]
