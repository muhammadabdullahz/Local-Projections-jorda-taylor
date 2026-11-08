"""Compare the Python estimates with the numbers printed in the Stata logs."""
import numpy as np
import pandas as pd
import config
import targets


def check_fig5(res5):
    b5, se5 = res5['b5'], res5['se5']

    chk5 = pd.DataFrame({'python_b': b5.values, 'stata_b': targets.stata_b5,
                         'python_se': se5, 'stata_se': targets.stata_se5}, index=b5.index)
    chk5['se_ratio'] = chk5['stata_se'] / chk5['python_se']

    print(f"Stacked obs: {res5['N5']} (Stata {targets.STATA_OBS5}) | T = {res5['T5']} (expect 86) | CORR = {res5['CORR5']:.4f}")
    print(f"Max |b diff|: {np.abs(chk5['python_b'] - chk5['stata_b']).max():.6f}")
    print(f"se ratio range: {chk5['se_ratio'].min():.4f} to {chk5['se_ratio'].max():.4f}")
    print(f"F = {res5['F5']:.2f} (Stata {targets.STATA_F5}) | p = {res5['pval5']:.3g}")
    print(f"mw = {res5['mw5']:.6f} (0.047764) | se(eta) = {res5['seta5']:.6f} (0.003062) | band = +/- {res5['band5']:.4f}")

    chk5.to_csv(config.TABLES_DIR / 'validation_fig5.csv')
    return chk5


def check_fig6(res6, INSTRUMENT6):
    b6, se6 = res6['b6'], res6['se6']

    if INSTRUMENT6 == 'RRCGShock':
        chk6 = pd.DataFrame({'python_b': b6, 'stata_b': targets.stata_b6,
                             'python_se': se6, 'stata_se': targets.stata_se6})
        chk6['se_ratio'] = chk6['stata_se'] / chk6['python_se']
        print(f"N = {res6['N6']} (Stata {targets.STATA_N6}) | chi2 = {res6['wald6']:.2f} (Stata {targets.STATA_CHI2_6})")
        print(f"Max |b diff|: {np.abs(chk6['python_b'] - chk6['stata_b']).max():.6f}")
        print(f"se ratio range: {chk6['se_ratio'].min():.4f} to {chk6['se_ratio'].max():.4f}")
        chk6.to_csv(config.TABLES_DIR / 'validation_fig6.csv')
        return chk6
    else:
        print("Validation skipped: Stata reference numbers exist only for RRCGShock.")
        return None
