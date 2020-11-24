import numpy as np
import os
import pandas as pd
from sklearn.linear_model import LinearRegression

from utility.config import paths
import utility.globals as glob


def iv_temperature_correction(overwrite=False):
    if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary_T_corr.xlsx')) and not overwrite:
        glob.df = pd.read_excel(os.path.join(paths['last_export'], 'IV_Summary_T_corr.xlsx'), index_col=[0, 1])
    else:
        if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary_T_corr.xlsx')):
            os.remove(os.path.join(paths['last_export'], 'IV_Summary_T_corr.xlsx'))
        glob.df.loc[:, ['isc_fit']] = glob.df['isc_fit'] * (1 + 0.0006 * (25 - glob.df['t_sample']))
        glob.df.loc[:, ['voc_fit']] = glob.df['voc_fit'] - 2.2 * (25 - glob.df['t_sample'])
        glob.df.loc[:, ['pmax_fit']] = glob.df['pmax_fit'] * (1 - 0.0045 * (25 - glob.df['t_sample']))
        glob.df.to_excel(os.path.join(paths['last_export'], 'IV_Summary_T_corr.xlsx'))


def iv_irradiance_fit(name, channel):
    mask = glob.df['name'] == name
    glob.irrad_fit_pars = list()
    y_pred = list()
    for key in ['isc_fit', 'voc_fit', 'pmax_fit']:
        x = glob.df[mask].dropna()[f'irrad{channel}'].values.reshape(-1, 1)  # values converts it into a numpy array
        y = glob.df[mask].dropna()[key].values.reshape(-1, 1)  # values converts it into a numpy array
        lin_reg = LinearRegression()  # create object for the class
        lin_reg.fit(x, y)  # perform linear regression
        y_pred.append(lin_reg.predict(x))
        glob.irrad_fit_pars.append([lin_reg.coef_[0, 0], lin_reg.intercept_[0]])
    return y_pred


def iv_irradiance_correction(channel, one_sun, overwrite):
    if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary_TI_corr.xlsx')) and not overwrite:
        glob.df = pd.read_excel(os.path.join(paths['last_export'], 'IV_Summary_TI_corr.xlsx'), index_col=[0, 1])
    else:
        if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary_TI_corr.xlsx')):
            os.remove(os.path.join(paths['last_export'], 'IV_Summary_TI_corr.xlsx'))
        glob.df.loc[:, ['isc_fit']] = glob.df['isc_fit'] + (glob.irrad_fit_pars[0][0] if glob.irrad_fit_pars[0][0] > 0
                                                            else 0) * (one_sun - glob.df[f'irrad{channel}'])
        glob.df.loc[:, ['voc_fit']] = glob.df['voc_fit'].values.reshape(-1, 1) + \
                                      (glob.irrad_fit_pars[1][0] if glob.irrad_fit_pars[1][0] > 0 else 0) * \
                                      (np.log(one_sun) - np.log(glob.df[f'irrad{channel}'].values.reshape(-1, 1)))
        glob.df.loc[:, ['pmax_fit']] = glob.df['pmax_fit'] + (glob.irrad_fit_pars[2][0] if glob.irrad_fit_pars[2][0] > 0
                                                              else 0) * (one_sun - glob.df[f'irrad{channel}'])
        glob.df.to_excel(os.path.join(paths['last_export'], 'IV_Summary_TI_corr.xlsx'))


def reference_fit(groups, xaxis):
    mask_mx = glob.df['group'].isin(groups)
    df_fit = glob.df[mask_mx].sort_values(by=xaxis)
    glob.irrad_fit_pars = list()
    y_pred = list()
    for key in ['isc_eff', 'pmax_eff']:
        x = df_fit[xaxis].values.reshape(-1, 1)  # values converts it into a numpy array
        y = df_fit[key].values.reshape(-1, 1)  # values converts it into a numpy array
        yerr = df_fit[f"d{key}"].values.reshape(-1, 1).flatten()  # values converts it into a numpy array
        lin_reg = LinearRegression()  # create object for the class
        lin_reg.fit(x, y, sample_weight=1/yerr)  # perform linear regression
        y_pred.append(lin_reg.predict(x))
        glob.irrad_fit_pars.append([lin_reg.coef_[0, 0], lin_reg.intercept_[0]])
    return y_pred
