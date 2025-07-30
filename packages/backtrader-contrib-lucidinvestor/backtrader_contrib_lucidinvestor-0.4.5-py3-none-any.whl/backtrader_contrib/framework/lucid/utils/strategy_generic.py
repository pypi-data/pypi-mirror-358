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

# Import the backtrader platform
from backtrader_contrib.framework.lucid.utils.portfolio import Portfolio
from backtrader_contrib.framework.lucid.utils.order_management import OrderManager
from collections import Counter


class StrategyGeneric(OrderManager):
    """
    base class for Lucid Strategies.
    Generic next() method manages orderbook execution and follow-up
    """
    params = dict(update_target=None,
                  brokersimulation=True
                  )

    def __init__(self, name=None, **kwargs):
        self.name = "StrategyGeneric_unnamed" if name is None else name
        self.portfolio = Portfolio(assets=self.p.update_target)
        super().__init__(**kwargs)

        df = self.cerebro.datasbyname
        # Extract the length of the 'array' attribute for each data feed
        lengths = {key: len(feed.array) for key, feed in df.items()}
        if len(set(lengths.values())) != 1:
            print("There is an issue with part of the data feed, and the desired backtesting period.")

            # Find the most common length
            length_counts = Counter(lengths.values())
            most_common_length = length_counts.most_common(1)[0][0]  # Get the most frequent length

            # Identify feeds that don't match the most common length
            outliers = {key: length for key, length in lengths.items() if length != most_common_length}
            print(f"Most common length of the data feed is: {most_common_length}")
            if outliers:
                print("Feeds that may be problematic (outliers):", outliers)

                # Find the outlier with the smallest length
                smallest_outlier_key = min(outliers, key=outliers.get)
                smallest_outlier_length = outliers[smallest_outlier_key]

                # Extract the starting date of the smallest outlier
                # smallest_outlier_feed = df[smallest_outlier_key]
                starting_date = self.datas[0].datetime.date(1-smallest_outlier_length)

                print(f"Outlier with the smallest length: {smallest_outlier_key} (Length: {smallest_outlier_length})")
                print(f"Starting date of the smallest outlier: {starting_date}")

                exit("We enforce a full alignment of data feeds "
                     "( aligned with backtrader - next() is triggered only when all feeds have at least 1 value). "
                     "Clean Exit().")

        return

    def next(self):
        msg = f"\n[{self.name} -> {__name__} -> next -> execute_orderbook]"
        msg_temp = self.execute_orderbook(self.portfolio)

        if len(msg_temp) > 0:
            msg = msg + msg_temp
            self.add_log('info', msg, data=self.data0)

        self.check_order_book()

        return

    def notify_order(self, order):
        msg = f'\n[{self.name} -> {__name__} -> notify_order]'

        msg = msg + '\n ; Asset: ' + order.data._name + ' ; Buy/Sell: ' + str(order.isbuy()) + \
              '/' + str(order.issell()) + ' ; Ref: ' + str(order.ref)

        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            msg = msg + '\n ; OrderStatus:Executed ; Buy/Sell: ' + str(
                order.isbuy()) + '/' + str(
                order.issell()) + ' ; Price:' + \
                  str(order.executed.price) + ' ; Total Order Value: ' + str(order.executed.value) + \
                  ' - Net liquidation value in asset currency: ' + \
                  str(self.get_netliquidationvalue(data_currency=order.p.data)) + ' ; Commission:' + \
                  str(order.executed.comm)

            self.add_log('info', msg, data=self.data0)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled]:
            msg = msg + '\n ; OrderStatus:Canceled'
            self.add_log('info', msg, data=self.data0)

        elif order.status in [order.Margin]:
            msg = msg + '\n ; OrderStatus:TriggeredMargin'
            self.add_log('info', msg, data=self.data0)

        elif order.status in [order.Rejected]:
            msg = msg + '\n ; OrderStatus:Rejected'
            self.add_log('info', msg, data=self.data0)

        return
