import io


def df_info(df):
    buf = io.StringIO()
    df.info(buf=buf)
    return buf.getvalue()
