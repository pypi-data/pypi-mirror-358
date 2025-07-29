from __future__ import (absolute_import, division, print_function, unicode_literals)
from backtrader_contrib.strategies.lucid.strategic_asset_allocation.fixed_target_allocations import \
    FixedTargetAllocation

from uis_allocation import UISAllocation


class UISPortfolio(FixedTargetAllocation):
    params = (
        ('lookback_window', None),
    )

    def __init__(self, name="UIS", analytics_name="UIS-OrderManager", **kwargs):
        """
        Initialize the Antifragile Asset Allocation strategy.

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

    symbols = ["SPY", "TLT"]
    # TIP will go down (become ‘bad’) with rising yields and/or rising (expected) inflation
    canary = ["TIP"]
    # offensive trades
    offensive_trades = ["SSO", "UWM", "QLD", 'URE', 'UBT', 'UST']

    #start_date = '2012-12-1'
    #end_date = '2022-12-1'

    # https://www.r-bloggers.com/2015/02/the-logical-invest-universal-investment-strategy-a-walk-forward-process-on-spy-and-tlt/
    start_date = '2002-11-30'
    end_date = '2015-1-1'

    # bull-bear 2022-09-30 to 2009-02-27
    # bear-bull 2018-10-31 to 2007-09-28
    # bull run 2018-10-31 to 2009-02-27
    # bear-bull-bear 2009-02-28 to 1999-12-31

    # https://seekingalpha.com/article/2714185-the-spy-tlt-universal-investment-strategy#hasComeFromMpArticle=false
    strategy_publication_date = '2014-11-26'

    for etf in symbols:  # +canary+offensive_trades:
        portf.add_asset(Asset(symbol=etf, currency='USD', allocation=0.0))

    strategy_param = {'assets': symbols,
                      'canary': canary,
                      'offensive_trade': False,
                      'nb_asset_in_portfolio': 2
                      }

    strategic_alloc = UISAllocation(**strategy_param)

    run_backtest(trading_strategy=UISPortfolio, lucid_allocator=strategic_alloc,
                 strategy_param=strategy_param,
                 update_target=portf, min_percent_deviation=float(1 / 100),
                 yahoo=False, store_yahoo_csv=False, start_date=start_date, end_date=end_date,
                 datadir=data_folderpath, print_pyfolio=False, plot_pyfolio=True, plot_bt_default=False,
                 live_start_date=strategy_publication_date)
