"""Figure 5a: pooled-style LP-OLS with Driscoll-Kraay SEs.
Figure 6a: joint LP-IV (2SLS at every horizon) with joint HAC SEs."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm, f as f_dist, chi2 as chi2_dist
import config


# =====================================================================
# FIGURE 5a
# =====================================================================
def resid5(y, X):
    return sm.OLS(y, sm.add_constant(X)).fit().resid


def estimate_fig5(df):
    H5, NLAGS5, NW5 = config.H5, config.NLAGS5, config.NW5
    outcome5, shock5 = config.OUTCOME5, config.SHOCK5
    controls5 = config.CONTROLS5

    lags5 = pd.concat(
        {f'{c}_L{l}': df[c].shift(l) for c in controls5 for l in range(1, NLAGS5 + 1)}, axis=1)

    # shock residualised ONCE on the h=0 sample (86 obs)
    tmp5 = pd.concat([df[shock5], lags5], axis=1).dropna()
    rz5 = resid5(tmp5[shock5], tmp5.drop(columns=shock5))

    pieces5 = []
    for h in range(H5 + 1):
        y5 = (df[outcome5].shift(-h) - df[outcome5].shift(1)).rename('y')
        dh5 = pd.concat([y5, lags5], axis=1).dropna()
        ry5 = resid5(dh5['y'], dh5.drop(columns='y'))
        z5 = rz5.loc[ry5.index]
        pieces5.append(pd.DataFrame({
            'h': h, 't': ry5.index.to_timestamp(),
            'y': (ry5 - ry5.mean()).values, 'z': (z5 - z5.mean()).values}))
    stack5 = pd.concat(pieces5, ignore_index=True)

    num5 = (stack5['y'] * stack5['z']).groupby(stack5['h']).sum()
    den5 = (stack5['z'] ** 2).groupby(stack5['h']).sum()
    b5 = num5 / den5
    stack5['e'] = stack5['y'] - stack5['h'].map(b5) * stack5['z']

    # ---------- Driscoll-Kraay covariance ----------
    M5 = (stack5.assign(m=stack5['z'] * stack5['e'])
                .pivot(index='t', columns='h', values='m')
                .sort_index().fillna(0).values)

    S5 = M5.T @ M5
    for l in range(1, NW5 + 1):
        G5 = M5[l:].T @ M5[:-l]
        S5 += (1 - l / (NW5 + 1)) * (G5 + G5.T)

    bread5 = np.diag(1 / den5.values)
    V5 = bread5 @ S5 @ bread5

    # ---------- small-sample correction (matches Stata's xtscc) ----------
    T5, N5, K5 = M5.shape[0], len(stack5), H5 + 2
    CORR5 = np.sqrt((T5 / (T5 - 1)) * ((N5 - 1) / (N5 - K5)))
    V5c = V5 * CORR5 ** 2
    se5 = np.sqrt(np.diag(V5c))

    # ---------- joint test ----------
    F5 = float(b5.values @ np.linalg.inv(V5c) @ b5.values / (H5 + 1))
    pval5 = f_dist.sf(F5, H5 + 1, 85)

    # ---------- significance band (blue dashed lines) ----------
    y05 = (df[outcome5] - df[outcome5].shift(1)).rename('y')
    d05 = pd.concat([y05, df[shock5], lags5], axis=1).dropna()
    Xc5 = sm.add_constant(d05.drop(columns=['y', shock5]))
    ry05 = sm.OLS(d05['y'], Xc5).fit().resid
    rz05 = sm.OLS(d05[shock5], Xc5).fit().resid
    mw5 = (rz05 ** 2).mean()
    eta5 = ry05 * rz05
    seta5 = sm.OLS(eta5, np.ones(len(eta5))).fit(
        cov_type='HAC', cov_kwds={'maxlags': NW5, 'use_correction': True}).bse.iloc[0]
    band5 = norm.ppf(1 - 0.05 / (2 * (H5 + 1))) * seta5 / mw5

    return {'b5': b5, 'se5': se5, 'band5': band5, 'F5': F5, 'pval5': pval5,
            'T5': T5, 'N5': N5, 'CORR5': CORR5, 'mw5': mw5, 'seta5': seta5}


# =====================================================================
# FIGURE 6a
# =====================================================================
def resid6(y, X):
    """OLS residuals of y on a constant and X, using only rows with no missing values."""
    dd = pd.concat([y.rename('y'), X], axis=1).dropna()
    Xc = np.column_stack([np.ones(len(dd)), dd[X.columns].to_numpy()])
    beta = np.linalg.lstsq(Xc, dd['y'].to_numpy(), rcond=None)[0]
    return pd.Series(dd['y'].to_numpy() - Xc @ beta, index=dd.index)


def estimate_fig6(df6, INSTRUMENT6=config.INSTRUMENT6):
    H6, NLAGS6, NW6 = config.H6, config.NLAGS6, config.NW6
    OUTCOME6, ENDOG6 = config.OUTCOME6, config.ENDOG6
    CTRL6 = config.CTRL6

    # ---------- residualise like Stata ----------
    ctrl6 = pd.concat(
        {f'{c}_L{l}': df6[c].shift(l) for c in CTRL6 for l in range(1, NLAGS6 + 1)}, axis=1)

    # outcome at each horizon (long difference), each residualised on ITS OWN sample
    ry6 = pd.concat(
        {f'y{h}': resid6(df6[OUTCOME6].shift(-h) - df6[OUTCOME6].shift(1), ctrl6)
         for h in range(H6 + 1)}, axis=1)

    # treatment and instrument, residualised once
    rffr6 = resid6(df6[ENDOG6], ctrl6).reindex(df6.index)
    rz6   = resid6(df6[INSTRUMENT6], ctrl6).reindex(df6.index)
    rzl6  = pd.concat({f'z{l}': rz6.shift(l) for l in range(1, NLAGS6 + 1)}, axis=1)

    # common sample for all 49 equations
    d6 = pd.concat([ry6, rffr6.rename('x'), rz6.rename('z0'), rzl6], axis=1).dropna()
    N6 = len(d6)

    Y6 = d6[[f'y{h}' for h in range(H6 + 1)]].to_numpy()                       # N x 49
    x6 = d6['x'].to_numpy()
    Z6 = np.column_stack([np.ones(N6), d6[['z0'] + list(rzl6.columns)].to_numpy()])   # N x 8
    X6 = np.column_stack([x6, np.ones(N6)])                                    # [ffr, constant]

    # ---------- 2SLS for every horizon ----------
    A6 = np.linalg.inv(Z6.T @ Z6 / N6)
    G6 = Z6.T @ X6 / N6                                                        # 8 x 2
    M6 = np.linalg.solve(G6.T @ A6 @ G6, G6.T @ A6)                            # 2 x 8
    theta6 = M6 @ (Z6.T @ Y6 / N6)                                             # 2 x 49
    b6 = theta6[0]                                                             # b_0 ... b_48

    # ---------- joint HAC covariance (Bartlett, 6 lags, no centering) ----------
    E6 = Y6 - X6 @ theta6
    m6 = (Z6[:, None, :] * E6[:, :, None]).reshape(N6, -1)                     # N x 392
    S6 = m6.T @ m6 / N6
    for l in range(1, NW6 + 1):
        Gl6 = m6[l:].T @ m6[:-l] / N6
        S6 += (1 - l / (NW6 + 1)) * (Gl6 + Gl6.T)

    B6 = np.kron(np.eye(H6 + 1), M6)                                           # 98 x 392
    V6 = B6 @ S6 @ B6.T / N6
    Vb6 = V6[0::2, 0::2]                                                       # cov of b_0 ... b_48
    se6 = np.sqrt(np.diag(Vb6))

    # ---------- joint test: all 49 b_h = 0 ----------
    wald6 = float(b6 @ np.linalg.solve(Vb6, b6))
    pval6 = chi2_dist.sf(wald6, H6 + 1)

    # ---------- first stage (non-robust F) ----------
    fs6 = np.linalg.lstsq(Z6, x6, rcond=None)[0]
    rss_u6, rss_r6 = ((x6 - Z6 @ fs6) ** 2).sum(), ((x6 - x6.mean()) ** 2).sum()
    F1_6 = ((rss_r6 - rss_u6) / 7) / (rss_u6 / (N6 - 8))

    print(f"Instrument: {INSTRUMENT6} | N = {N6} | sample {d6.index[0]} to {d6.index[-1]}")
    print(f"Wald chi2(49) = {wald6:.2f} | p = {pval6:.3g} | first-stage F (non-robust) = {F1_6:.1f}")

    return {'b6': b6, 'se6': se6, 'wald6': wald6, 'pval6': pval6, 'F1_6': F1_6, 'N6': N6}
