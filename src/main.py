"""Run the whole replication: raw data -> estimates -> validation -> figures and tables."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))   # lets the modules import each other

import pandas as pd
import config
import data_prep
import lp_tools
import validate
import plots


def main():
    # ===================== FIGURE 5a =====================
    print("=" * 20, "FIGURE 5a", "=" * 20)
    raw, df, long_names = data_prep.load_fig5_data()
    data_prep.describe_data(raw, df)
    plots.plot_eda5(raw, long_names)

    res5 = lp_tools.estimate_fig5(df)
    validate.check_fig5(res5)
    plots.plot_fig5(res5['b5'], res5['se5'], res5['band5'], res5['pval5'])

    pd.DataFrame({'b': res5['b5'].values, 'se': res5['se5']},
                 index=res5['b5'].index).to_csv(config.TABLES_DIR / 'irf_fig5.csv')

    # ===================== FIGURE 6a =====================
    print("=" * 20, "FIGURE 6a", "=" * 20)
    raw6, df6 = data_prep.load_fig6_data()
    plots.plot_eda6(raw6)

    res6 = lp_tools.estimate_fig6(df6, config.INSTRUMENT6)
    validate.check_fig6(res6, config.INSTRUMENT6)
    plots.plot_fig6(res6['b6'], res6['se6'], res6['wald6'], res6['pval6'], AS_PUBLISHED=True)
    plots.plot_fig6(res6['b6'], res6['se6'], res6['wald6'], res6['pval6'], AS_PUBLISHED=False)

    pd.DataFrame({'b': res6['b6'], 'se': res6['se6']}).to_csv(config.TABLES_DIR / 'irf_fig6.csv')

    print("Done. Tables in", config.TABLES_DIR, "| figures in", config.FIGURES_DIR)


if __name__ == '__main__':
    main()
