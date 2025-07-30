from __future__ import (absolute_import, division, print_function, unicode_literals)
from backtrader_contrib.strategies.lucid.strategic_asset_allocation.fixed_target_allocations import \
    FixedTargetAllocation

from daa_allocation import DAAModel


class RotationPortfolio(FixedTargetAllocation):
    """
    Breadth Momentum and the Canary Universe: Defensive Asset Allocation (DAA)
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3212862
    +
    https://indexswingtrader.blogspot.com/2018/12/exploring-smart-leverage-daa-on-steroids.html
    https://finimize.com/content/tactical-asset-allocation-part-one-sidestep-crashes-defensive-strategy


    Reproduced. Performance: on 2025.3.16 ; https://indexswingtrader.blogspot.com/2018/07/announcing-defensive-asset-allocation.html
    Rolling 3Y: 2.44% ; Rolling 1Y: 0.79%

    Not Reproduced: https://drive.google.com/drive/folders/1V0C3IHuPrc6_uUaOdXM9zYJ3iWZFqzfD
    DAA-G12 T6B1 R12 C3 P2 (VWO,BND)
    Signals: SPY,QQQ,IWM,VGK,EWJ,VWO,GSG,GLD,VNQ,HYG, LQD,TLT + C2:SHY,IEF
    Trades: SSO,QLD,UWM,VGK,EWJ,VWO,GSG,GLD,URE,HYG,LQD,UBT + C2:SHY,UST
    31-10-2013 to 31-10-2018: 19.12%, MDD: -6.52%, Sharpe: 1.17

    Not Reproduced: DAA-G12 T6B1 R12 C2 P2 (VWO,BND)
    Signals: SPY,QQQ,IWM,VGK,EWJ,VWO,GSG,GLD,VNQ,HYG,TLT,LQD + C2:SHY,IEF
    Trades: SPY,QQQ,IWM,VGK,EWJ,VWO,GSG,GLD,VNQ,HYG,TLT,LQD + C2:SHY,IEF
    '2009-2-27' to '2019-2-1' (bull run 10y): R = 11.96%, MDD = -5.72%, Sharpe = 1.49
    """
    params = (
        ('lookback_window', None),
    )

    def __init__(self, name="Rotation", analytics_name="Rotation-OrderManager", **kwargs):
        """
        Args:
            kwargs : dict
                Additional keyword arguments passed to the parent class.
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

    # Risky (denoted eg. R12 when there are N=NR=12 risky assets),
    symbol_g12 = ["SPY", "QQQ", "IWM", "VGK", "EWJ", "VWO", "GSG", "GLD", "VNQ", "HYG", "TLT", "LQD"]
    symbol_g4 = ["SPY", "VEA", "VWO", "BND"]

    # Cash (eg. C3 for NC=3 cash/bonds assets).
    defensive_c3 = ["SHY", "IEF", "LQD"]
    defensive_c2 = ["SHY", "IEF"]

    # Protective (eg. P2, with NP=2 canary assets)
    canary_p2 = ["VWO", "BND"]

    # offensive trades
    offensive_trades = ["SSO", "UWM", "QLD", 'URE', 'UBT', 'UST']

    # strategy type
    daa_g12 = symbol_g12 + canary_p2 + defensive_c3 #+ offensive_trades
    daa_g12_T = 6
    daa_g12_B = 2
    # https://indexswingtrader.blogspot.com/2018/12/exploring-smart-leverage-daa-on-steroids.html
    # DAA-G12 T6B1 R12 C2 P2 (VWO,BND)
    # Signals: SPY,QQQ,IWM,VGK,EWJ,VWO,GSG,GLD,VNQ,HYG,TLT,LQD + C2:SHY,IEF
    # Trades: SPY,QQQ,IWM,VGK,EWJ,VWO,GSG,GLD,VNQ,HYG,TLT,LQD + C2:SHY,IEF
    daa_g12_1 = symbol_g12 + canary_p2 + defensive_c2
    daa_g12_1_T = 6
    daa_g12_1_B = 1

    daa_g12_c3 = symbol_g12 + canary_p2 + defensive_c3

    daa_g4 = symbol_g4 + canary_p2 + defensive_c2
    daa_g4_T = 3; daa_g4_B = 1

    start_date = '2009-2-27'  # not leveraged: '2009-2-27' ; leveraged: '2011-2-27'
    end_date = '2019-2-1'
    # bull-bear 2022-09-30 to 2009-02-27
    # bear-bull 2018-10-31 to 2007-09-28
    # bull run 2018-10-31 to 2009-02-27
    # bear-bull-bear 2009-02-28 to 1999-12-31
    strategy_publication_date = '2018-7-1'

    all_assets = daa_g12_1 #+ offensive_trades
    for etf in all_assets:
        portf.add_asset(Asset(symbol=etf, currency='USD', allocation=0.0))

    # there are two free parameters ie. the (risky) top T and
    # the breadth parameter B (which determines the cash fraction, given the canary breadth)
    strategy_param = {'assets': symbol_g12,
                      'cash_proxy': defensive_c2,
                      'canary': canary_p2,
                      'offensive_trade': False,
                      'nb_asset_in_portfolio': daa_g12_1_T,
                      'breadth_parameter': daa_g12_1_B,
                      }

    strategic_alloc = DAAModel(**strategy_param)

    run_backtest(trading_strategy=RotationPortfolio, lucid_allocator=strategic_alloc,
                 strategy_param=strategy_param,
                 update_target=portf, min_percent_deviation=float(1 / 100),
                 yahoo=False, store_yahoo_csv=False, start_date=start_date, end_date=end_date,
                 datadir=data_folderpath, print_pyfolio=False, plot_pyfolio=True, plot_bt_default=False,
                 live_start_date=strategy_publication_date)
