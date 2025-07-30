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

import math
# Import the backtrader platform
import backtrader as bt
from backtrader_contrib.framework.lucid.utils.analytics import Analytics


class OrderManager(Analytics, bt.Strategy):
    """
    Simple base class for managing strategy order designed from the perspective of backtesting on daily data, yet
    to be easily overloaded
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.buys = dict()
        self.sells = dict()
        self.order_book = list()

        self.ready_to_execute = False  # track whether the rebalance orderbook is ready for execution
        return

    def cansubmitorder(self):
        if len(self.order_book) == 0:
            return True
        else:
            return False

    def get_netliquidationvalue(self, data_currency=None):
        """
            Temporary Fix to facilitate getting currency-specific net liquidation value of the Portfolio
            Default to normal behavior if data feed is not from a live Store (i.e. IBStore).

            Why not a complete implementation: refer to
            https://gitlab.com/algorithmic-trading-library/backtrader_contrib/-/issues/9
        """
        #
        if data_currency is None or not(hasattr(data_currency, 'contract')):
            return self.broker.getvalue()

    def execute_orderbook(self, portfolio):
        msg = ""
        if self.cansubmitorder() and self.ready_to_execute:
            msg = msg + f"\n[{self.analytics_name} -> {__name__} -> execute_orderbook:initiate rebalancing]"

            if len(self.sells) + len(self.buys) > 0:
                msg = msg + "\n sending sell orders"

                # portfolio total cash value in BASE currency
                pf_value = self.get_netliquidationvalue()

                for asset in self.sells:
                    currency = portfolio.assets[asset].currency
                    allocation = portfolio.allocation_by_currency[currency] * self.sells[asset]
                    # round decimals down
                    decimals = 2
                    factor = 10 ** decimals
                    allocation = math.floor(allocation * factor) / factor
                    self.order_target_percent(data=asset, target=allocation)
                    # self.order_target_value(data=asset, target=allocation*pf_value)
                msg = msg + "\n sending buy orders"
                self.sells = dict()

                for asset in self.buys:
                    currency = portfolio.assets[asset].currency
                    allocation = portfolio.allocation_by_currency[currency] * self.buys[asset]
                    # round decimals down
                    decimals = 2
                    factor = 10 ** decimals
                    allocation = math.floor(allocation * factor) / factor
                    self.order_target_percent(data=asset, target=allocation)
                    # self.order_target_value(data=asset, target=allocation*pf_value)
                msg = msg + "\n buy and sell orders have been sent out"
                self.buys = dict()

                # all orders were submitted. No other orders to manage until next rebalancing.
                self.ready_to_execute = False

        return msg

    def get_execution_setup(self, k):
        data = self.datas[self.getdatanames().index(k)]
        exectype = None  # market order
        price = None  # end of day adj.close - cerebro.broker.set_coc(True)
        price_dict = {'sell': data.close[0], 'buy': data.close[0]}
        return data, exectype, price, price_dict

    def check_order_book(self, logoutput=False):
        '''
        https://www.backtrader.com/docu/order.html

        Created: 0
        Submitted: 1 sent to the broker and awaiting confirmation
        Accepted: 2 accepted by the broker
        Partial: 3 partially executed
        Completed: 4 fully exexcuted
        Canceled/Cancelled: 5 canceled by the user
        Expired: 6 expired
        Margin: 7 not enough cash to execute the order.
        Rejected: 8 Rejected by the broker
        :return: Integer ob_size = len(self.order_book)
        '''

        msg_error = list()
        msg_warning = list()
        msg_info = list()

        for o in self.order_book:
            try:

                if o.status in [bt.Order.Completed]:
                    msg_info.append('\n OrderStatus:COMPLETED ; Buy/Sell: ' + str(
                        o.isbuy()) + '/' + str(
                        o.issell()) + ' ; Size: ' +
                                    str(o.executed.size) + ' ; Price: ' +
                                    str(o.executed.price) + ' ; Value: ' + str(o.executed.value) +
                                    ' ; Comm: ' + str(o.executed.comm) + ' ; OrderRef: ' + str(o.ref)
                                    )
                    # 'remove' removes the first matching value, not a specific index
                    # Remove all completed Orders
                    self.order_book.remove(o)
                    pass

                elif o.status in [bt.Order.Accepted, bt.Order.Partial]:
                    pass

                elif o.status in [bt.Order.Expired]:
                    msg_info.append('\n OrderStatus:EXPIRED: Buy/Sell: ' + str(o.isbuy()) + '/' + str(
                        o.issell()) + ' - Size: ' + \
                                    ' - Ref: ' + str(o.ref)
                                    )

                    # 'remove' removes the first matching value, not a specific index
                    # Remove all completed Orders
                    self.order_book.remove(o)

                elif o.status in [bt.Order.Rejected, bt.Order.Cancelled, bt.Order.Margin]:
                    # broker could reject order if not enough cash

                    msg_warning.append('\n OrderStatus:Rejected/Cancelled/Margin; < ORDER HAS BEEN ' + str(
                        o.status) + ' - Total cash: ' + str(
                        self.broker.getcash()) + \
                                       ' - Total Value (BASE): ' + str(self.get_netliquidationvalue()) + ">" +
                                       ' - Net liquidation value in asset currency: ' +
                                       str(self.get_netliquidationvalue(data_currency=o.p.data))
                                       )
                    self.order_book.remove(o)
                    pass

                #elif not o.alive():
                #    self.order_book.remove(o)
                #    msg_info.append('\n < Removing order (not alive) ' + str(o) + ' from order_book >')

            except AttributeError as error:
                msg_error.append('\n bt-contrib:order_management > AttributeError: ' + str(error) +
                                 '\n-> Might be testing (is fakebroker activated?) - removing order from queue to '
                                 'continue execution')
                self.order_book.remove(o)

        if logoutput and len(msg_warning) > 0:
            for msg in msg_warning:
                self.add_log('warning', msg, data=self.data0)
        if logoutput and len(msg_info) > 0:
            for msg in msg_info:
                self.add_log('info', msg, data=self.data0)
        if logoutput and len(msg_error) > 0:
            for msg in msg_error:
                self.add_log('error', msg, data=self.data0)

        return msg_warning, msg_info, msg_error
