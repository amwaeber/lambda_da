import os
import pandas as pd

from utility.config import paths
import utility.globals as glob


def average_by_experiment(overwrite=False):
    if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary_Average.xlsx')) and not overwrite:
        glob.df = pd.read_excel(os.path.join(paths['last_export'], 'IV_Summary_Average.xlsx'), index_col=0)
    else:
        if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary_Average.xlsx')):
            os.remove(os.path.join(paths['last_export'], 'IV_Summary_Average.xlsx'))
        glob.df = glob.df.groupby(level=0).agg({'timestamp': 'first', 'isc_fit': ['mean', 'std'],
                                                'voc_fit': ['mean', 'std'], 'pmax_fit': ['mean', 'std'],
                                                'name': 'first', 'film_id': 'first', 't_room': 'first',
                                                'rh_room': 'first', 'datetime': 'first'})
        glob.df.columns = ['timestamp', 'isc', 'disc', 'voc', 'dvoc', 'pmax', 'dpmax', 'name', 'film_id',
                           't_room', 'rh_room', 'datetime']
        glob.df.to_excel(os.path.join(paths['last_export'], 'IV_Summary_Average.xlsx'))


def average_by(col_name, overwrite=False):
    if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary_Average_by_Film.xlsx')) and not overwrite:
        glob.df = pd.read_excel(os.path.join(paths['last_export'], 'IV_Summary_Average_by_Film.xlsx'), index_col=0)
    else:
        if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary_Average_by_Film.xlsx')):
            os.remove(os.path.join(paths['last_export'], 'IV_Summary_Average_by_Film.xlsx'))
        mask_unique = glob.df[col_name].isin(glob.df[col_name].value_counts()[glob.df[col_name].
                                             value_counts() == 1].index)
        df_unique = glob.df[mask_unique]
        df_to_average = glob.df[~mask_unique]
        df_to_average = df_to_average.groupby(col_name).agg({'timestamp': 'first', 'isc': ['mean', 'std'],
                                                             'voc': ['mean', 'std'], 'pmax': ['mean', 'std'],
                                                             'name': 'first', 'film_id': 'first', 't_room': 'mean',
                                                             'rh_room': 'mean', 'datetime': 'first'})
        df_to_average.columns = ['timestamp', 'isc', 'disc', 'voc', 'dvoc', 'pmax', 'dpmax', 'name', 'film_id',
                                 't_room', 'rh_room', 'datetime']
        glob.df = pd.concat([df_unique, df_to_average]).sort_values(by='datetime')
        glob.df = glob.df.reset_index(drop=True)
        glob.df.to_excel(os.path.join(paths['last_export'], 'IV_Summary_Average_by_Film.xlsx'))


def calc_efficiency(name, overwrite=False):
    if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary_Efficiency.xlsx')) and not overwrite:
        glob.df = pd.read_excel(os.path.join(paths['last_export'], 'IV_Summary_Efficiency.xlsx'), index_col=0)
    else:
        if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary_Efficiency.xlsx')):
            os.remove(os.path.join(paths['last_export'], 'IV_Summary_Efficiency.xlsx'))
        dut_pmax, dut_dpmax = glob.df[glob.df['name'] == name][['pmax', 'dpmax']].values[0]
        upper = ((glob.df['pmax'] + glob.df['dpmax']) / (dut_pmax - dut_dpmax) - 1) * 100
        lower = ((glob.df['pmax'] - glob.df['dpmax']) / (dut_pmax + dut_dpmax) - 1) * 100
        glob.df['pmax_eff'] = (upper + lower) / 2
        glob.df['dpmax_eff'] = (upper - lower) / 2
        dut_isc, dut_disc = glob.df[glob.df['name'] == name][['isc', 'disc']].values[0]
        upper = ((glob.df['isc'] + glob.df['disc']) / (dut_isc - dut_disc) - 1) * 100
        lower = ((glob.df['isc'] - glob.df['disc']) / (dut_isc + dut_disc) - 1) * 100
        glob.df['isc_eff'] = (upper + lower) / 2
        glob.df['disc_eff'] = (upper - lower) / 2
        glob.df.to_excel(os.path.join(paths['last_export'], 'IV_Summary_Efficiency.xlsx'))


def pce_vs_reference(groups, xaxis):
    for group_id in groups:
        mask_group = glob.df['group'] == group_id
        for i, key in enumerate(['isc_eff', 'pmax_eff']):
            glob.df.loc[mask_group, [f"{key[:-3]}impr"]] = glob.df[mask_group][key] - \
                                            (glob.irrad_fit_pars[i][0] * glob.df[mask_group][xaxis] +
                                             glob.irrad_fit_pars[i][1])
            glob.df.loc[mask_group, [f"d{key[:-3]}impr"]] = glob.df[mask_group][f"d{key}"]
    glob.df.to_excel(paths['pv_improve_file'])
