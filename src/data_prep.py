"""Load the two Excel sheets and cut the estimation samples."""
import pandas as pd
import config


def load_fig5_data():
    # The sheet has two header rows: row 1 = long names, row 2 = mnemonics, data from row 3
    header_rows = pd.read_excel(config.DATA_PATH, sheet_name=config.SHEET5, header=None, nrows=2)
    raw = pd.read_excel(config.DATA_PATH, sheet_name=config.SHEET5, header=1)   # mnemonic row as column names

    raw = raw.rename(columns={raw.columns[0]: 'date'})
    raw.columns = raw.columns.str.strip()

    # Dates look like '1960q1' -> quarterly PeriodIndex
    raw.index = pd.PeriodIndex(raw['date'].astype(str).str.upper(), freq='Q')
    raw = raw.drop(columns='date')

    # Dictionary of long names (for plot titles)
    long_names = dict(zip(header_rows.iloc[1, 1:], header_rows.iloc[0, 1:]))

    # Stata cuts the sample BEFORE building lags/leads, so we do the same
    df = raw.loc[config.SAMPLE5_START:config.SAMPLE5_END].copy()

    # Scale to percent, as in the .do file (dlcpi and dlrgdp are left as they are)
    df['lcpi']  = 100 * df['lcpi']
    df['lrgdp'] = 100 * df['lrgdp']

    print("Observations in sample:", len(df))   # should be 92
    return raw, df, long_names


def describe_data(raw, df):
    print("Missing values, full data:")
    print(raw.isna().sum(), "\n")

    print("Missing values, estimation sample:")
    print(df.isna().sum(), "\n")

    print(df.describe().round(3))


def load_fig6_data():
    raw6 = pd.read_excel(config.DATA_PATH, sheet_name=config.SHEET6, header=1)
    raw6 = raw6.rename(columns={raw6.columns[0]: 'date'})
    raw6.columns = raw6.columns.str.strip()

    # Dates look like '1965m12'
    ym = raw6['date'].astype(str).str.lower().str.split('m', expand=True).astype(int)
    raw6.index = pd.PeriodIndex(year=ym[0], month=ym[1], freq='M')
    raw6 = raw6.drop(columns='date')

    # Cut the sample BEFORE building lags/leads (same as Stata)
    df6 = raw6.loc[config.SAMPLE6_START:config.SAMPLE6_END].copy()
    print("Observations (expect 181):", len(df6))
    print(df6[['urate', 'infl', 'ffr', 'RRCGShock', 'KuttnerShock']].isna().sum())
    return raw6, df6
