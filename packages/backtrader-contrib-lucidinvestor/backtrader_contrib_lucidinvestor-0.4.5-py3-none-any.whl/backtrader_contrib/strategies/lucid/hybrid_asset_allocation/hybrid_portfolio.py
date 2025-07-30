from __future__ import (absolute_import, division, print_function, unicode_literals)
from backtrader_contrib.strategies.lucid.strategic_asset_allocation.fixed_target_allocations import \
    FixedTargetAllocation

from hybrid_allocation import HybridAllocation
import math


class HybridPortfolio(FixedTargetAllocation):
    params = (
        ('lookback_window', None),
    )

    def __init__(self, name="HAA", analytics_name="HAA-OrderManager", **kwargs):
        """
        Initialize the HAA strategy.

        REPRODUCED:
            Fig 17 Comparison of HAA-Balanced with BAA-Balanced, and HAA-Simple with 60/40 (SPY/IEF)

        """

        super().__init__(name=name, analytics_name=analytics_name, **kwargs)
        msg = self.set_log_option(logconsole=True, level=1)
        self.add_log('info', msg)

        return


if __name__ == "__main__":
    from backtrader_contrib.framework.lucid.utils.run_backtest import run_backtest
    from backtrader_contrib.framework.lucid.utils.portfolio import Portfolio, Asset
    import pathlib
    import os

    p = pathlib.Path(__file__).parent.parent.parent.resolve()
    parent_bt_contrib = str(p.parent.parent.parent)
    data_folderpath = os.path.join(parent_bt_contrib, 'data/as_traded')

    if not os.path.exists(data_folderpath):
        msg = f"\nThe path {data_folderpath} to load the data in the backtest does not exist on this system. " \
              f"\nTo solve this issue, you may modify {__file__} as follows:" \
              f"\n  (1) Update the variable 'data_folderpath', " \
              f"\n  (2) or set 'yahoo=True' in run_backtest() provided this is for personal use and you have read " \
              f"and agreed to Yahoo's terms of use at https://policies.yahoo.com/us/en/yahoo/terms/index.htm."
        exit(msg)

    portf = Portfolio()

    symbols = ["SPY", "IWM", "EFA", "EEM", "VNQ", "IEF", "TLT"]

    offensive1 = ["SPY"]
    offensive4 = offensive1 + ["VEA", "VNQ", "IEF"]
    # US Equities: large cap S&P 500 (SPY) and small cap Russell 2000 (IWM)
    # Foreign Equities: developed markets (VEA) and emerging markets (VWO)
    # Alternative Assets: commodities (DBC) and US real estate (VNQ)
    # US Bonds: 7-10y Treasury (IEF) and 20y Treasury (TLT)
    offensive8 = offensive4 + ["IWM", "VWO", "DBC", "TLT"]
    offensive9 = offensive8 + ["QQQ"]
    offensive12 = offensive9 + ["VGK", "EWJ", "GLD", "LQD"]
    offensive12.remove("VEA")
    offensive16 = offensive12 + ['IWD', 'VGK', 'SCZ', 'REM', 'HYG']
    # Refining ETF Asset Momentum Strategy: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095447
    # For stock ETFs we chose SPDR S&P 500 ETF Trust (SPY), iShares Russell 2000 ETF (IWM),
    # iShares MSCI EAFE ETF (EFA), iShares MSCI Emerging Markets ETF (EEM), iShares U.S. Real Estate ETF (IYR),
    # Invesco QQQ Trust (QQQ)
    offensive_vojtko = ["SPY", "IWM", "EFA", "EEM", "IYR", "QQQ"]
    # lucid
    offensive_lucid = ["SPY", "DBC", "QQQ"]
    # defensive assets
    defensive1 = ["BIL"]
    defensive2 = defensive1 + ["IEF"]
    defensive0 = ["TLT", "GLD", "BND"]
    # For bond ETFs we chose iShares iBoxx Investment Grade Corporate Bond ETF (LQD),
    # iShares 7-10 Year Treasury Bond ETF (IEF), iShares TIPS Bond ETF (TIP). Lastly we included
    # Invesco CurrencyShares Euro Currency Trust (FXE) as the currency ETF
    defensive3 = ["LQD", "IEF", "TIP", "FXE"]
    # TIP will go down (become ‘bad’) with rising yields and/or rising (expected) inflation
    canary = ["TIP"]
    # offensive trades
    offensive_trades = ["SSO", "UWM", "QLD", 'URE', 'UBT', 'UST']

    start_date = '2012-12-1'
    end_date = '2022-12-1'
    # bull-bear 2022-09-30 to 2009-02-27
    # bear-bull 2018-10-31 to 2007-09-28
    # bull run 2018-10-31 to 2009-02-27
    # bear-bull-bear 2009-02-28 to 1999-12-31
    strategy_publication_date = '2022-1-1'

    offensive_assets = offensive1
    cash_proxy = defensive2

    haa_U1T1 = {"offensive": offensive1, "defensive": defensive2, "canary": canary, "T": 1}
    haa_G8T4 = {"offensive": offensive8, "defensive": defensive2, "canary": canary, "T": 4}
    haa_G12T6 = {"offensive": offensive12, "defensive": defensive2, "canary": canary, "T": 6}

    haa_setup = haa_G8T4
    for etf in haa_setup["offensive"]+haa_setup["defensive"]+haa_setup["canary"]+offensive_trades:
        portf.add_asset(Asset(symbol=etf, currency='USD', allocation=0.0))

    strategy_param = {'offensive_assets': haa_setup["offensive"],
                      'offensive_trade': False,
                      'cash_proxy': haa_setup["defensive"],
                      'canary': haa_setup["canary"][0],
                      'fast_mom': False,
                      'nb_asset_in_portfolio': haa_setup["T"]  # math.floor((1+len(offensive_assets))/2)
                      }

    strategic_alloc = HybridAllocation(**strategy_param)

    run_backtest(trading_strategy=HybridPortfolio, lucid_allocator=strategic_alloc,
                 strategy_param=strategy_param,
                 update_target=portf, min_percent_deviation=float(1 / 100),
                 yahoo=False, store_yahoo_csv=False, start_date=start_date, end_date=end_date,
                 datadir=data_folderpath, print_pyfolio=False, plot_pyfolio=True, plot_bt_default=False,
                 live_start_date=strategy_publication_date)
