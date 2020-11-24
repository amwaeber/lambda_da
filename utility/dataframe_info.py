import io


def df_info(df):
    buf = io.StringIO()
    df.info(buf=buf)
    return buf.getvalue()


def pv_explore_groups(df):
    grp_idx = 0
    grp_info = list()
    while grp_idx in df['group'].unique():
        df_grp = df[df['group'] == grp_idx]
        entry = [None, str(grp_idx)]
        for col in ['Matrix', 'QD Type', 'Nominal Emission (nm)', 'QD Concentration (mg/g)', 'Solvent',
                    'Additives', 'Additive concentration (%)']:
            entry.append(str(df_grp[col].fillna('None').mode()[0]))
        entry.append(str(df_grp['Manufactured'].values[0]).split('T')[0])
        entry.append(str(df_grp['datetime'].values[0]).split('T')[0])
        grp_info.append(entry)
        grp_idx += 1
    return grp_info
