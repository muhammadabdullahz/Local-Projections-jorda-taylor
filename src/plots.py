"""EDA charts and Figures 5a / 6a. Adjustable plot settings sit at the top of each function."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
import config


def plot_eda5(raw, long_names):
    vars_to_plot = ['lcpi', 'dlcpi', 'rr_shock', 'stir', 'dstir', 'dlrgdp']

    fig, axes = plt.subplots(2, 3, figsize=(15, 7))
    for ax, v in zip(axes.flat, vars_to_plot):
        raw[v].plot(ax=ax, color='steelblue', lw=1.5)
        ax.axvline(pd.Period('1985Q1', 'Q'), color='gray', ls='--')   # sample start
        ax.axvline(pd.Period('2007Q4', 'Q'), color='gray', ls='--')   # sample end
        ax.set_title(long_names.get(v, v), fontsize=10)
        ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / 'eda_fig5.png', dpi=200)
    plt.show()


def plot_eda6(raw6):
    fig, axes = plt.subplots(2, 2, figsize=(12, 6))
    for ax, v in zip(axes.flat, ['urate', 'infl', 'ffr', 'RRCGShock']):
        raw6[v].plot(ax=ax, color='steelblue', lw=1.5)
        ax.axvline(pd.Period('1985-01', 'M'), color='gray', ls='--')
        ax.axvline(pd.Period('2000-01', 'M'), color='gray', ls='--')
        ax.set_title(v); ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / 'eda_fig6.png', dpi=200)
    plt.show()


def plot_fig5(b5, se5, band5, pval5):
    # ---------- plot settings: edit these ----------
    FIG_SIZE   = (5, 6.2)
    COLOR      = 'green'
    Y_LIM      = (-6, 2.5)
    Y_TICKS    = range(-6, 3, 2)
    X_TICKS    = [0, 5, 10, 15]
    MAX_H      = 16            # Stata plots t = 0..16
    SHOW_BAND  = True          # blue dashed significance bands
    TITLE      = ''            # e.g. 'Figure 5a: CPI response to Romer-Romer shock'
    SAVE_PATH  = config.FIGURES_DIR / 'Figure5a_python.png'

    c95 = norm.ppf(0.975)
    p5 = pd.DataFrame({'b': b5.values, 'se': se5}, index=b5.index).loc[:MAX_H]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.fill_between(p5.index, p5.b - c95 * p5.se, p5.b + c95 * p5.se, color=COLOR, alpha=0.10, lw=0)  # 95%
    ax.fill_between(p5.index, p5.b - p5.se, p5.b + p5.se, color=COLOR, alpha=0.20, lw=0)              # 68%
    ax.plot(p5.index, p5.b, color=COLOR, lw=3)
    ax.axhline(0, color='black', lw=1)
    if SHOW_BAND:
        ax.axhline(band5, color='blue', ls='--', lw=1)
        ax.axhline(-band5, color='blue', ls='--', lw=1)
    ax.set_xticks(X_TICKS); ax.set_yticks(list(Y_TICKS)); ax.set_ylim(*Y_LIM)
    ax.set_xlabel('Horizon, quarters, $h$'); ax.set_ylabel('Response, log CPI x100')
    ax.text(8, 2.2, f'p-value of joint significance test: {pval5:.3g}', ha='center', fontsize=8)
    if TITLE:
        ax.set_title(TITLE, fontsize=10)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(SAVE_PATH, dpi=200)
    plt.show()


def plot_fig6(b6, se6, wald6, pval6, AS_PUBLISHED=True):
    # ---------- plot settings: edit these ----------
    # AS_PUBLISHED = True : published figure (b1..b48 drawn at t=0..47, an off-by-one in the .do file)
    # AS_PUBLISHED = False: b0..b47 drawn at their true horizons
    FIG_SIZE   = (5, 5)
    COLOR      = 'blue'
    Y_LIM      = (-1, 2.7)
    Y_TICKS    = [-1, 0, 1, 2]
    X_TICKS    = range(0, 49, 12)
    MAX_T      = 48         # Stata plots t < 48
    TITLE      = ''         # e.g. 'Figure 6a: Unemployment response (LP-IV)'
    SAVE_PATH  = config.FIGURES_DIR / ('Figure6a_python_'
                                       + ('published' if AS_PUBLISHED else 'corrected') + '.png')
    # -----------------------------------------------

    t6   = np.arange(MAX_T)
    idx6 = np.arange(1, MAX_T + 1) if AS_PUBLISHED else np.arange(0, MAX_T)
    bp6, sp6 = b6[idx6], se6[idx6]

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.fill_between(t6, bp6 - sp6, bp6 + sp6, color=COLOR, alpha=0.10, lw=0)               # 68%: lighter
    ax.fill_between(t6, bp6 - 1.96 * sp6, bp6 + 1.96 * sp6, color=COLOR, alpha=0.20, lw=0) # 95%: darker
    ax.plot(t6, bp6, color=COLOR, ls='--', lw=3)
    ax.axhline(0, color='black', lw=1)
    ax.set_xticks(list(X_TICKS)); ax.set_yticks(Y_TICKS); ax.set_ylim(*Y_LIM)
    ax.set_xlabel('Horizon, months, $h$'); ax.set_ylabel('Response, percentage points')
    ax.text(24, 2.5, rf'Joint test: $\chi^2$(49) = {wald6:.1f} ($p$ = {pval6:.3f})',
            ha='center', fontsize=8)
    if TITLE:
        ax.set_title(TITLE, fontsize=10)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(SAVE_PATH, dpi=200)
    plt.show()
