#!/usr/bin/env python
# Copyright 2023 LucidInvestor <https://lucidinvestor.ca/>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import (absolute_import, division, print_function, unicode_literals)
from backtrader_contrib.strategies.lucid.strategic_asset_allocation.fixed_target_allocations import \
    FixedTargetAllocation

from backtrader_contrib.strategies.lucid.adaptive_asset_allocation.adaptive_allocation import AdaptiveAllocation


class AdaptiveAssetAllocation(FixedTargetAllocation):

    def __init__(self, name="AdaptiveAssetAllocation", analytics_name="AdaptiveAssetAllocation-OrderManager", **kwargs):
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

    ###############################################
    # Build the Asset Allocation Portfolio object #
    ###############################################
    portf = Portfolio()

    """
    Original: Adaptive Asset Allocation: A Primer - see paper in folder /lit.review
    a review paper of the strategy in 2013. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2328254
    """
    # symbols = ['SPY', 'EWJ', 'IYR', 'RWX', 'TLT', 'IEF', 'EEM', 'EFA', 'GLD', 'DBC']
    # strategy_publication_date = '2013-1-1'
    #start_date = '2006-4-1'
    
    """
    Original extended: https://investresolve.com/dynamic-asset-allocation-for-practitioners-part-1-universe-selection/
    
    DBC: Commodities (DB Liquid Commodities Index)
    GLD: Gold Bullion
    SPY: U.S. Stocks (S&P 500)
    EFA: European Stocks (FTSE Europe Index)
    VPL: Asia Pacific Stocks (MSCI Asia Pacific)
    EEM: Emerging Market Stocks (FTSE EM)
    RWX: Global REITs (Dow Jones Global REITs Index)
    IEF: Intermediate Treasuries (Barclays 7-10 Year Treasury Index)
    TLT: Long Treasuries (Barclays 20+ Year Treasury Index)
    GVI (BWX): Intermediate International Government Bonds (Unhedged)
    PCY (2007) EMB (2008) : USD Denominated Emerging Market Bonds
    TIP: Long-Term TIPs
    """
    #symbols = ['DBC', 'GLD', 'SPY', 'EFA', 'VPL', 'EEM', 'RWX', 'IEF', 'TLT', 'GVI', 'PCY', 'TIP', 'QQQ']
    #strategy_publication_date = '2018-1-1'
    #start_date = '2007-11-1'

    """
    Original simplified: https://www.recipeinvesting.com/article-the-adaptive-asset-allocation-portfolio-how-to-maximize-return-using-minimum-variance-and-momentum/
    The 9 asset classes are as follows: U.S. Large Cap Equity, U.S. Small Cap Equity, NASDAQ 100 Equity,
    U.S. Real Estate, U.S. Long Term Treasury Bonds, Emerging Markets Equity, International Developed Markets Equity,
    Gold, and Commodities.
    """
    symbols = ['SPY', 'IWM', 'QQQ', 'IYR', 'TLT', 'EEM', 'EFA', 'GLD', 'DBC']
    # We have been tracking variations of the Adaptive Asset Allocation Portfolio since 2014 at recipeinvesting.com.
    strategy_publication_date = '2014-1-1'
    start_date = '2006-11-1'

    """
    Original extended 2: http://www.the-lazy-trader.com/2015/01/ETF-Rotation-Systems-to-beat-the-Market-SPY-IWM-EEM-EFA-TLT-TLH-DBC-GLD-ICF-RWX.html
    """
    #symbols = ['SPY', 'IWM', 'TLT', 'TLH', 'EEM', 'EFA', 'GLD', 'DBC', 'ICF', 'RWX']
    #strategy_publication_date = '2015-1-19'
    #start_date = '2006-4-1'

    for etf in symbols:
        asset = Asset(symbol=etf, currency='USD', allocation=0.0)
        portf.add_asset(asset)

    # --------------------------------------------------
    # or load the Asset Allocation Portfolio from json #
    # --------------------------------------------------
    """
    json_input = "aaa_simplified.json"
    with open(json_input) as json_file:
        update_target = json.load(json_file)
    portf = Portfolio(asset_as_dict=update_target)
    """
    # ---------------------------------------------------------------------
    # DATA FORMAT: .csv                                                   #
    # date	close	volume	Open	high	low                           #
    # 2000-12-28	92.889801	8358700	132.8125	133.875	132.59375     #
    # ---------------------------------------------------------------------

    end_date = '2023-8-1'

    strategy_param = {'momentum_window': 180,
                      'volatility_window': 20,
                      'nb_asset_in_portfolio': 5}

    strategic_alloc = AdaptiveAllocation(**strategy_param)

    run_backtest(trading_strategy=AdaptiveAssetAllocation, lucid_allocator=strategic_alloc,
                 strategy_param=strategy_param,
                 update_target=portf, min_percent_deviation=float(1 / 100),
                 yahoo=False, store_yahoo_csv=False, start_date=start_date, end_date=end_date,
                 datadir=data_folderpath,
                 print_pyfolio=False, plot_pyfolio=True, plot_bt_default=False,
                 live_start_date=strategy_publication_date
                 )
