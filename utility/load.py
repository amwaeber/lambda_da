from datetime import datetime
import os
import pandas as pd

from utility.config import paths
import utility.globals as glob


def load_experiments(path, overwrite=True):
    if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary.xlsx')) and not overwrite:
        glob.df = pd.read_excel(os.path.join(paths['last_export'], 'IV_Summary.xlsx'), index_col=[0, 1])
    else:
        if os.path.exists(os.path.join(paths['last_export'], 'IV_Summary.xlsx')):
            os.remove(os.path.join(paths['last_export'], 'IV_Summary.xlsx'))
        df_list = []
        df_keys = []
        for subdir, dirs, files in os.walk(path):
            for filename in files:
                if filename == 'IV_Summary.xlsx':
                    filepath = subdir + os.sep + filename
                    df_list.append(pd.read_excel(filepath))
                    df_keys.append(os.path.basename(subdir).split(' ')[0])
        glob.df = pd.concat(df_list, keys=df_keys)
        df_list.clear()
        glob.df.drop(columns=['Unnamed: 0', 'count', 'cycle', 'cell_id', 'location', 'cal_date', 'cal_value', 'pid_pb',
                     'pid_int', 'pid_der', 'pid_fuoc', 'pid_tcr1', 'pid_tcr2', 'pid_sp'],
                     inplace=True)
        glob.df['datetime'] = [datetime.fromtimestamp(ts) for ts in glob.df['timestamp'].values]
        glob.df.to_excel(os.path.join(paths['last_export'], 'IV_Summary.xlsx'))


def load_film_database():
    return pd.read_excel(paths['film_db'])
