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

import datetime
from datetime import timedelta

from backtrader_contrib.framework.lucid.utils.strategy_generic import StrategyGeneric
from backtrader_contrib.strategies.lucid.strategic_asset_allocation.strategic_allocation import StrategicAllocation
import math


class FixedTargetAllocation(StrategyGeneric):
    """
    Strategic asset allocation SAA is a portfolio strategy whereby the investor sets target allocations for various
    asset classes and rebalances the portfolio periodically, or when the asset allocation weights materially deviate
    from the strategic asset allocation weights due to unrealized gains/losses in each asset class.

    Example of established SAA are:
        - 2 Assets:
            60% in equities for the good times, 40% in bonds for the bad (and for the yield).
            . e.g portfolio: 60% VTI, 40% BND or 60% SPY, 40% TLT
            > ref: https://seekingalpha.com/article/4522459-ignore-market-forecasts-and-adopt-an-all-weather-portfolio
            > ref: Fig.5, p.10 https://www.vanguard.ca/documents/investment-principles-wp.pdf
            > ref: https://advisors.vanguard.com/insights/article/likethephoenixthe6040portfoliowillriseagain
            > ref: https://www.quantifiedstrategies.com/60-40-portfolio-strategy/

        - 5 Assets:
            Ray Dalio all weather portfolio: 55% U.S. bonds, 30% U.S. stocks, and 15% hard assets (Gold + Commodities)
            . e.g. portfolio: 40% TLT + 15% IEF, 30% VTI, 7.5% GLD + 7.5% DBC
            > ref: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4021133
            > ref: https://seekingalpha.com/article/4522459-ignore-market-forecasts-and-adopt-an-all-weather-portfolio
            > ref: https://www.nasdaq.com/articles/remember-all-weather-portfolio-its-having-killer-year-2016-09-27
            > ref: https://www.atlantis-press.com/article/125966027.pdf

    StrategyGeneric class info.
    As for any backtrader strategy, input parameters can be used in instances of the class by accessing the member
    variable self.params (shorthand: self.p)

    :Example:
    cerebro.addstrategy(FixedTargetAllocation)

    .. todo:: this is just a test for sphinx
    """

    params = dict(
        min_percent_deviation=float(0.0 / 100)  # minimum percent deviation from current to trigger a re-allocation
    )

    def __init__(self, lucid_allocator, name="FixedTargetAllocation",
                 analytics_name="FixedTargetAllocation-OrderManager", **kwargs):

        super().__init__(name=name, analytics_name=analytics_name, **kwargs)
        msg = self.set_log_option(logconsole=True, level=1)
        self.add_log('info', msg)

        # schedule function
        # Note: If 'when' is either SESSION_START or SESSION_END and tzdata is None, the 1st data feed in the system
        # (aka self.data0) will be used as the reference to find out the session times.

        self.lucid_allocator = lucid_allocator
        if not hasattr(self.cerebro, 'input_datadir'):
            self.cerebro.input_datadir = None
        self.lucid_allocator.set_lucid_taa(self.datas, csv_path=self.cerebro.input_datadir,
                                           lookback_window=self.lucid_allocator.set_lookback_window())

        # backtesting on EOD data
        self.offset_live = timedelta(minutes=0, hours=0)

        # To keep track of pending orders
        self.no_rebalance_action = False
        return

    def start(self):
        """
        **Note** (as per comments in code): add_timer can be called during ``__init__`` or ``start``
        :return:
        """
        # todo: seems that: time is replayed even for live trading (so if one is past time, it will be triggered)
        # todo: seems that: monthcarry=True is triggered on day 2also if we are on day 2, and the system did not see day 1
        # todo: check how the monthcarry and when/timer are set. it seems this is "replayed"
        # seem to validate live that there is a problem of logic with monthcarry in live mode ... if true it will always trigger at first run
        self.add_timer(when=datetime.time(hour=9, minute=00),
                       offset=self.offset_live,
                       # repeat=datetime.timedelta(minutes=1),
                       tzdata=self.data0,
                       monthdays=[1], monthcarry=True,
                       cheat=False,
                       name='rebalance_period'
                       )

    def notify_timer(self, timer, when, *args, **kwargs):
        msg = f'\n[{self.name} -> {__name__} -> notify_timer] - Time is (when parameter/variable) ' + str(when)
        if timer.kwargs['name'] == 'rebalance_period':
            msg = msg + '\n ---------------------- \n >>>>> REBALANCING TIME \n ----------------------'
            self.add_log('info', msg, data=self.data0)
            self.rebalance()
        return

    def allocation_to_int(self, _allocation):
        # Truncate to ≤100 and ensure no floating-point errors
        return min(int(100 * _allocation), 100)  # Cap at 100

    def allocate_portfolio(self, updated_allocation):
        # Reset all allocations to 0
        for asset in self.portfolio.assets:
            self.portfolio.assets[asset].allocation = 0.0

        total_allocated = 0

        for asset, allocation in updated_allocation.items():
            if allocation < 0:
                raise ValueError("Allocations cannot be negative.")

            # Convert allocation to integer percentage (capped at 100)
            norm_al = self.allocation_to_int(allocation)

            # Calculate remaining available weight
            remaining = 100 - total_allocated

            # If no space left, skip or break
            if remaining <= 0:
                break

            # Assign the lesser of norm_al or remaining space
            assigned = min(norm_al, remaining)
            self.portfolio.assets[asset].allocation = assigned / 100
            total_allocated += assigned

        # Optional: Warn if total < 100%
        if total_allocated < 100:
            self.add_log('info', f"Warning: Total allocations = {total_allocated}% (<100%)", data=self.data0)

    def rebalance(self):
        """
        Rebalance the portfolio.

        :return:
        """
        # Get the adjusted window of data and compute allocation
        updated_allocation = self.lucid_allocator.assign_equal_weight(today_date=self.datas[0].datetime.date())

        # Apply portfolio allocations
        self.allocate_portfolio(updated_allocation)

        msg = f"\n[{self.name} -> {__name__} -> rebalance]"

        self.buys = dict()
        self.sells = dict()

        # ------------------------------- NOTE -------------------------------------
        # update portfolio allocations as needed.                                  |
        # strategic asset allocation > self.portfolio is fixed - no update needed. |
        # --------------------------------------------------------------------------

        for a in self.portfolio.assets.keys():  # displays all keys in list
            msg = msg + "\n Asset: " + str(a)

            currency = self.portfolio.assets[a].currency
            price_close = self.datas[self.getdatanames().index(a)].close[0]
            acc_value = self.get_netliquidationvalue(data_currency=self.datas[self.getdatanames().index(a)])

            desired_value = acc_value * self.portfolio.assets.get(a).allocation * \
                            self.portfolio.allocation_by_currency[currency]

            current_value = self.getposition(data=self.datas[self.getdatanames().index(a)]).size * price_close

            msg = msg + "\n __ current_value = " + str(current_value)
            msg = msg + "\n __ desired_value = " + str(desired_value)

            if abs(current_value-desired_value)/acc_value <= self.p.min_percent_deviation:
                # do nothing: rebalancing is less than minimum percent deviation
                msg = msg + f"\n __ DO NOTHING. rebalancing is less than minimum percent deviation of " \
                            f"{self.p.min_percent_deviation}%"

            elif current_value > desired_value and abs(current_value-desired_value) > price_close:
                self.sells.update({a: self.portfolio.assets.get(a).allocation})
                msg = msg + "\n __ order is a SELL"
                msg = f"{msg} {str(a)} | {str(100 * self.portfolio.assets.get(a).allocation)}% " \
                      f"(manually fixed) > rebalancing position (updated at time of order) by " \
                      f"{str((desired_value - current_value) / self.datas[self.getdatanames().index(a)].close[0])} " \
                      f"shares"

            elif current_value < desired_value and abs(current_value-desired_value) > price_close:
                self.buys.update({a: self.portfolio.assets.get(a).allocation})
                msg = msg + "\n __ order is a BUY"
                msg = f"{msg} {str(a)} | {str(100 * self.portfolio.assets.get(a).allocation)}% " \
                      f"(manually fixed) > rebalancing position (updated at time of order) by " \
                      f"{str((desired_value - current_value) / self.datas[self.getdatanames().index(a)].close[0])} " \
                      f"shares"

            else:
                # do nothing: rebalancing is less than the price of an action even though min_percent_deviation
                # check was passed (maybe it's set to 0)
                msg = msg + f"\n __ DO NOTHING. rebalancing is less than the price of an action even though " \
                            f"minimum percent deviation check was passed (maybe set to 0)."

        self.add_log('info', msg, data=self.data0)

        if len(self.buys) + len(self.sells) == 0:
            self.no_rebalance_action = True
        else:
            self.ready_to_execute = True
        return


if __name__ == "__main__":
    from backtrader_contrib.framework.lucid.utils.run_backtest import run_backtest
    from backtrader_contrib.framework.lucid.utils.portfolio import Portfolio, Asset
    import pathlib
    import os

    p = pathlib.Path(__file__).parent.parent.parent.resolve()
    parent_bt_contrib = str(p).split('backtrader_contrib/backtrader_contrib')[0]
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
    spy = Asset(symbol='SPY', currency='USD', allocation=0.6)
    tlt = Asset(symbol='TLT', currency='USD', allocation=0.4)
    portf = Portfolio()
    portf.add_asset(spy)
    portf.add_asset(tlt)
    # --------------------------------------------------
    # or load the Asset Allocation Portfolio from json #
    # --------------------------------------------------
    """json_input = "60-40.json"
    with open(json_input) as json_file:
        update_target = json.load(json_file)
    portf = Portfolio(asset_as_dict=update_target)"""

    start_date = '2007-1-1'
    end_date = '2023-3-1'

    # ---------------------------------------------------------------------
    # DATA FORMAT: .csv                                                   #
    # date	close	volume	Open	high	low                           #
    # 2000-12-28	92.889801	8358700	132.8125	133.875	132.59375     #
    # ---------------------------------------------------------------------
    strategy_param = {
        'nb_asset_in_portfolio': 2,
        'fixed_weights': portf
    }
    # Fixed strategic allocation (e.g., 60% SPY, 40% TLT)
    strategic_alloc = StrategicAllocation(**strategy_param)

    run_backtest(trading_strategy=FixedTargetAllocation, lucid_allocator=strategic_alloc, update_target=portf,
                 min_percent_deviation=float(1/100),
                 yahoo=False, store_yahoo_csv=False, start_date=start_date, end_date=end_date,
                 datadir=data_folderpath, strategy_param=strategy_param,
                 print_pyfolio=False, plot_pyfolio=True, plot_bt_default=False
                 )
