from __future__ import (absolute_import, division, print_function, unicode_literals)
from backtrader_contrib.strategies.lucid.strategic_asset_allocation.fixed_target_allocations import \
    FixedTargetAllocation

from sector_rotation_momentum import SectorRotationMomentumTopn
from sector_rotation_giordano import SectorRotationGiordano


class AntifragileAssetAllocation(FixedTargetAllocation):
    params = (
        ('lookback_window', None),
    )

    def __init__(self, name="Antifragile", analytics_name="Antifragile-OrderManager", **kwargs):
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

    # 'XLC': 2018 ; 'XLRE': 2015 # not in sector list
    SP500_11Sector = ['XLY', 'XLP', 'XLE', 'XLF', 'XLV', 'XLI', 'XLB', 'XLK', 'XLU', 'VOX', 'RWR']

    symbols = ['SPY',
               # 'UUP', 'DBA', 'DBC'
               #'QQQ',  'GLD',
               'XLY', 'XLP', 'XLE', 'XLF', 'XLV', 'XLI', 'XLB', 'XLK', 'XLU', 'VOX', 'RWR'
               ]
    # symbols = ['SPY', 'IWM', 'QQQ', 'IYR', 'TLT', 'EEM', 'EFA', 'GLD', 'DBC']

    Canary = ['SPY', 'TLT']

    # https://www.sectorspdrs.com/
    SP500Sector = ['XLE', 'XLU', 'XLK', 'XLB', 'XLP', 'XLY', 'XLI', 'XLV', 'XLF',
                   # 'XLRE', 'XLC',  # 2015, 2018
                   ]
    hedge = ['FXY', 'FXF', 'GLD', 'IEF', 'SH', 'TLT', 'SHY']

    strategy_publication_date = '2019-1-1'
    # The final part illustrates the results of a model backtesting, represented through
    # monthly performances from June 2004 to February 2019
    start_date = '2005-10-1'  # '2005-9-1' fit to VOX 2004.9.29 missing data # hedge '2007-9-1'
    end_date = '2019-2-1'

    symbols = SP500_11Sector + ['SPY', 'SHY', 'TLT'] #+ hedge

    for etf in symbols:
        portf.add_asset(Asset(symbol=etf, currency='USD', allocation=0.0))

    # Rotation strategy

    # strategy_param = {
    #     'lookback_3m': 63,
    #     'lookback_6m': 126,
    #     'lookback_12m': 252,
    #     'nb_asset_in_portfolio': 3,
    # }
    # strategic_alloc = SectorRotationMomentum(**strategy_param)


    """
    strategy_param = {
        'lookback_3m': 63,
        'lookback_6m': 126,
        'lookback_12m': 252,
        'sma_10m': 210,
        'nb_asset_in_portfolio': 3,
    }
    strategic_alloc = SectorRotationMomentumTopn(**strategy_param)
    """

    """
    strategy_param = {
        'lookback_3m': 63,
        'lookback_6m': 126,
        'lookback_12m': 252,
        'sma_10m': 210,
        'momentum_4m': 84,
        'nb_asset_in_portfolio': 5,
    }

    strategic_alloc = AntiFragileSectorRotationMomentum(**strategy_param)
    """


    strategy_param = {
        'assets': SP500_11Sector,
        'hedge': [],
        'nb_asset': len(SP500_11Sector),
        'momentum_window': 4*21,
        'volatility_window': 21,
        'correlation_window': 4*21,
        'atr_window': 42,
        'high_period': 63,
        'low_period': 105,
        'nb_asset_in_portfolio': 5,
        'hedge_asset': 'TLT',
        'momentum_weight': 0.6,
        'volatility_weight': 0.2,
        'correlation_weight': 0.2,
        'atr_weight': 0  # todo: OHLC
    }
    strategic_alloc = SectorRotationGiordano(**strategy_param)


    run_backtest(trading_strategy=AntifragileAssetAllocation, lucid_allocator=strategic_alloc,
                 strategy_param=strategy_param,
                 update_target=portf, min_percent_deviation=float(1 / 100),
                 yahoo=False, store_yahoo_csv=False, start_date=start_date, end_date=end_date,
                 datadir=data_folderpath, print_pyfolio=True, plot_pyfolio=True, plot_bt_default=False,
                 live_start_date=strategy_publication_date)
