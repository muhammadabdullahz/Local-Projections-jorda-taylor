"""Paths, sample windows, lags and variable names for both figures."""
from pathlib import Path

# ---------- paths ----------
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / 'data' / 'raw' / 'JT2025_Data.xlsx'
TABLES_DIR = ROOT / 'outputs' / 'tables'
FIGURES_DIR = ROOT / 'outputs' / 'figures'
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Figure 5a: LP-OLS, CPI response to the Romer-Romer shock ----------
SHEET5 = 'Ex5'
SAMPLE5_START, SAMPLE5_END = '1985Q1', '2007Q4'
H5, NLAGS5, NW5 = 17, 6, 17
OUTCOME5, SHOCK5 = 'lcpi', 'rr_shock'
CONTROLS5 = ['dlrgdp', 'dlcpi', 'dstir']

# ---------- Figure 6a: LP-IV, unemployment response to an FFR shock ----------
SHEET6 = 'Ex6'
SAMPLE6_START, SAMPLE6_END = '1985-01', '2000-01'
H6, NLAGS6, NW6 = 48, 6, 6
INSTRUMENT6 = 'RRCGShock'            # 'KuttnerShock' for the extension (validation then skipped)
OUTCOME6, ENDOG6 = 'urate', 'ffr'
CTRL6 = ['urate', 'infl', 'ffr']
