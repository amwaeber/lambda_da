import os
import pandas as pd

from utility.config import paths
import utility.globals as glob
from utility.load import load_film_database


def drop_experiments(indices):
    for idx in indices:
        mask = glob.df.index.get_level_values(0).str.endswith(str(idx).zfill(3))
        glob.df = glob.df[~mask]


def select_experiment_range(idxmin, idxmax):
    mask = (glob.df.index.get_level_values(0).str[-3:].astype(int) >= idxmin) & \
           (glob.df.index.get_level_values(0).str[-3:].astype(int) <= idxmax)
    glob.df = glob.df[mask]


def merge_film_db(overwrite=False):
    if os.path.exists(os.path.join(paths['last_export'], 'Processed_IV.xlsx')) and not overwrite:
        glob.df = pd.read_excel(os.path.join(paths['last_export'], 'Processed_IV.xlsx'), index_col=0)
    else:
        if os.path.exists(os.path.join(paths['last_export'], 'Processed_IV.xlsx')):
            os.remove(os.path.join(paths['last_export'], 'Processed_IV.xlsx'))
        df_film = load_film_database()
        glob.df = pd.merge(glob.df, df_film, left_on='film_id', right_on='Film ID', how='left')
        glob.df.drop(columns=['Film ID', 'Film Length (mm)', 'Film width (mm)', 'Comment'], inplace=True)

        glob.df['group'] = glob.df['Matrix'].astype(str) + glob.df['Solvent'].astype(str) + \
                           glob.df['QD Type'].astype(str) + glob.df['QD Batch'].astype(str) + \
                           glob.df['QD Manufacturer'].astype(str) + glob.df['QD Concentration (mg/g)'].astype(str) + \
                           glob.df['Nominal Emission (nm)'].astype(str) + glob.df['Manufactured'].astype(str)
        glob.df['group'] = glob.df['group'].astype('category')
        glob.df['group'] = glob.df['group'].cat.codes

        glob.df.to_excel(os.path.join(paths['last_export'], 'Processed_IV.xlsx'))


def merge_processed_data(filepath1, filepath2, output_path):
    df1 = pd.read_excel(filepath1, index_col=0)
    df2 = pd.read_excel(filepath2, index_col=0)

    df1['group'] = df1['group'].astype(str) + '-1'
    df2['group'] = df2['group'].astype(str) + '-2'

    df_merged = pd.concat([df1, df2]).sort_values(by='datetime')
    df_merged['group'] = df_merged['group'].astype('category')
    df_merged['group'] = df_merged['group'].cat.codes
    df_merged = df_merged.reset_index(drop=True)

    save_path = os.path.join(output_path, 'Processed_IV.xlsx')
    while os.path.exists(save_path):
        save_path = save_path[:-5] + '(1).xlsx'

    df_merged.to_excel(save_path)
