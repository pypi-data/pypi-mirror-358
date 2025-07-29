#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)
import pathlib
import os
from datetime import date, datetime
import pandas as pd

import unittest

from backtrader_contrib.framework.lucid.data import data_adjuster as btadj


class TestingTimeAdjutedClose(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestingTimeAdjutedClose, self).__init__(*args, **kwargs)
        self.csv_path = pathlib.Path(__file__).parent
        self.assets_list = ["AAPL"]
        self.data = btadj.DataBundle(assets_list=self.assets_list, csv_path=self.csv_path.joinpath('data'))

    def test_as_traded(self):
        """
        This test represents the as traded prices of AAPL prior all split corporate events
        :return:
        """
        self.data.sliding_start_date = "2014-05-15"
        self.data.sliding_end_date = "2014-08-01"

        adjusted_data = self.data.get_adjusted_window(manual_window=True)
        as_traded = self.data.as_traded_prices['AAPL']
        close_price = adjusted_data['AAPL']
        ydata = self.data.as_traded_prices['AAPL'].RawClose

        # May 15th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-05-15').tz_localize('America/New_York')]
                               , 2), 588.82)
        # May 30th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-05-30').tz_localize('America/New_York')]
                               , 2), 633)
        # June 6th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-06-06').tz_localize('America/New_York')]
                               , 2), 645.57)
        # June 9th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-06-09').tz_localize('America/New_York')]
                               , 2), 655.9)
        # June 13th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-06-13').tz_localize('America/New_York')]
                               , 2), 91.28)
        # June 13th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-06-13').tz_localize('America/New_York')]
                               , 2), 91.28)
        # Aug 31st 2020
        self.assertEqual(round(ydata[pd.Timestamp('2020-08-31').tz_localize('America/New_York')]
                               , 2), 516.16)
        # 28 February 2005
        self.assertEqual(round(ydata[pd.Timestamp('2005-02-28').tz_localize('America/New_York')]
                               , 2), 89.72)
        # 21 June 2000
        self.assertEqual(round(ydata[pd.Timestamp('2000-06-21').tz_localize('America/New_York')]
                               , 2), 111.25)
        # 1st November 1999
        self.assertEqual(round(ydata[pd.Timestamp('1999-11-01').tz_localize('America/New_York')]
                               , 2), 77.62)
        # 16 June 1987 (79$)
        # https://sundaresansekar.medium.com/if-you-had-1-share-of-apple-in-1987-heres-how-much-it-s-worth-now-d22b6b273546
        self.assertEqual(round(ydata[pd.Timestamp('1987-06-15').tz_localize('America/New_York')]
                               , 2), 78.5)

    def test_time_window_adj_close(self):
        """
        This test represents the information provided by Quantopian on their lookback adjusted prices:
        Lookback windows now use prices that are split-, merger-, and dividend-adjusted.

        source: https://web.archive.org/web/20190215100332/https://www.quantopian.com/quantopian2/adjustments
        :return:
        """


        """
        AAPL's price change from July 1 to August 1, 2014
        """
        d0 = date(2014, 7, 1)
        d1 = date(2014, 8, 1)
        delta = d1 - d0  # delta.days

        self.data.set_sliding_window(lookback=delta.days)
        self.data.sliding_start_date = "2014-07-01"
        self.data.sliding_end_date = "2014-08-01"

        adjusted_data = self.data.get_adjusted_window(manual_window=True)
        close_price = adjusted_data['AAPL']

        # from the perspective of July 1, 2014? This is easy $93.52
        self.assertEqual(round(close_price[0]
                               , 2), 93.52)

        # On August 1st the as-traded price was $96.13
        self.assertEqual(round(close_price[-1]
                               , 2), 96.13)

        # There are no events between July 1 and August 1, so we can use the as-traded prices.
        # The price increased 2.7%.
        pct_change = 100 * (close_price[-1] - close_price[0]) / close_price[0]
        self.assertTrue(2.6 < pct_change < 2.8)

        """
        AAPL's adjusted price from May 15 to August 1, 2014
        To make that calculation useful, we first adjust the historical prices in our lookback windows. The price
        adjustment allows us to compare prices across splits and dividends. The adjusted price for May 15 is
        ($588.82/7), or $84.12. That enables us to calculate the percent change in AAPL from May 15, 2014 to
        August 1, 2014 to be 14.3%.
        """

        d0 = date(2014, 5, 15)
        d1 = date(2014, 8, 1)
        delta = d1 - d0  # delta.days

        self.data.set_sliding_window(lookback=delta.days)
        self.data.sliding_start_date = "2014-05-15"
        self.data.sliding_end_date = "2014-08-01"

        adjusted_data = self.data.get_adjusted_window(manual_window=True)
        close_price = adjusted_data['AAPL']

        # After adjustment, calculate the percent change in AAPL from May 15, 2014 to August 1, 2014 to be 14.3%
        pct_change = 100 * (close_price[-1] - close_price[0]) / close_price[0]
        self.assertTrue(14.2 < pct_change < 14.3)

    def test_sliding_window_adj_close(self):
        """
        This test represents the information provided by Quantopian on their lookback adjusted prices:
        Lookback windows now use prices that are split-, merger-, and dividend-adjusted.

        You can now make accurate calculations of the returns of securities because the price information in the
        lookback window is fully adjusted. When your algorithm calls for historical data using history() or in
        pipeline calculations, the data is returned to the algorithm with prices adjusted to the date of simulation.

        source: https://web.archive.org/web/20190215100332/https://www.quantopian.com/quantopian2/adjustments
        :return:
        """

        d0 = date(2014, 5, 15)
        d1 = date(2014, 8, 1)
        delta = d1 - d0  # delta.days

        self.data.set_sliding_window(lookback=delta.days)

        self.data.set_sliding_window(lookback=delta.days)
        self.data.sliding_start_date = "2014-05-15"
        self.data.sliding_end_date = "2014-08-01"

        adjusted_data = self.data.get_adjusted_window(manual_window=True)
        close_price = adjusted_data['AAPL']

        # May 15th Price
        self.assertEqual(round(close_price[0], 2), 84.12)
        # May 30th price
        self.assertEqual(round(close_price[pd.Timestamp('2014-05-30').tz_localize('America/New_York')]
                               , 2), 90.43)
        # June 6th price
        self.assertEqual(round(close_price[pd.Timestamp('2014-06-06').tz_localize('America/New_York')]
                               , 2), 92.22)
        # June 9th price
        self.assertEqual(round(close_price[pd.Timestamp('2014-06-09').tz_localize('America/New_York')]
                               , 2), 93.7)
        # June 13th price
        self.assertEqual(round(close_price[pd.Timestamp('2014-06-13').tz_localize('America/New_York')]
                               , 2), 91.28)


class TestingTimeAdjutedCloseFromYahoo(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestingTimeAdjutedCloseFromYahoo, self).__init__(*args, **kwargs)
        self.csv_path = pathlib.Path(__file__).parent
        self.assets_list = ["AAPL"]
        # default: downloaded yahoo data is not stored locally
        self.data = btadj.DataBundle(assets_list=self.assets_list)

        # verify that no csv as been stored
        all_files = os.listdir(self.csv_path)
        csv_files = list(filter(lambda f: f.endswith('.csv'), all_files))
        self.assertTrue(len(csv_files) == 0)

    def test_as_traded(self):
        """
        This test represents the as traded prices of AAPL prior all split corporate events
        :return:
        """
        self.data.sliding_start_date = "2014-05-15"
        self.data.sliding_end_date = "2014-08-01"

        adjusted_data = self.data.get_adjusted_window(manual_window=True)
        as_traded = self.data.as_traded_prices['AAPL']
        close_price = adjusted_data['AAPL']
        ydata = self.data.as_traded_prices['AAPL'].RawClose

        # May 15th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-05-15').tz_localize('America/New_York')]
                               , 2), 588.82)
        # May 30th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-05-30').tz_localize('America/New_York')]
                               , 2), 633)
        # June 6th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-06-06').tz_localize('America/New_York')]
                               , 2), 645.57)
        # June 9th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-06-09').tz_localize('America/New_York')]
                               , 2), 655.9)
        # June 13th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-06-13').tz_localize('America/New_York')]
                               , 2), 91.28)
        # June 13th Price
        self.assertEqual(round(as_traded['RawClose'][pd.Timestamp('2014-06-13').tz_localize('America/New_York')]
                               , 2), 91.28)
        # Aug 31st 2020
        self.assertEqual(round(ydata[pd.Timestamp('2020-08-31').tz_localize('America/New_York')]
                               , 2), 516.16)
        # 28 February 2005
        self.assertEqual(round(ydata[pd.Timestamp('2005-02-28').tz_localize('America/New_York')]
                               , 2), 89.72)
        # 21 June 2000
        self.assertEqual(round(ydata[pd.Timestamp('2000-06-21').tz_localize('America/New_York')]
                               , 2), 111.25)
        # 1st November 1999
        self.assertEqual(round(ydata[pd.Timestamp('1999-11-01').tz_localize('America/New_York')]
                               , 2), 77.62)
        # 16 June 1987 (79$)
        # https://sundaresansekar.medium.com/if-you-had-1-share-of-apple-in-1987-heres-how-much-it-s-worth-now-d22b6b273546
        self.assertEqual(round(ydata[pd.Timestamp('1987-06-15').tz_localize('America/New_York')]
                               , 2), 78.5)

    def test_time_window_adj_close(self):
        """
        This test represents the information provided by Quantopian on their lookback adjusted prices:
        Lookback windows now use prices that are split-, merger-, and dividend-adjusted.

        source: https://web.archive.org/web/20190215100332/https://www.quantopian.com/quantopian2/adjustments
        :return:
        """


        """
        AAPL's price change from July 1 to August 1, 2014
        """
        d0 = date(2014, 7, 1)
        d1 = date(2014, 8, 1)
        delta = d1 - d0  # delta.days

        self.data.set_sliding_window(lookback=delta.days)
        self.data.sliding_start_date = "2014-07-01"
        self.data.sliding_end_date = "2014-08-01"

        adjusted_data = self.data.get_adjusted_window(manual_window=True)
        close_price = adjusted_data['AAPL']

        # from the perspective of July 1, 2014? This is easy $93.52
        self.assertEqual(round(close_price[0]
                               , 2), 93.52)

        # On August 1st the as-traded price was $96.13
        self.assertEqual(round(close_price[-1]
                               , 2), 96.13)

        # There are no events between July 1 and August 1, so we can use the as-traded prices.
        # The price increased 2.7%.
        pct_change = 100 * (close_price[-1] - close_price[0]) / close_price[0]
        self.assertTrue(2.6 < pct_change < 2.8)

        """
        AAPL's adjusted price from May 15 to August 1, 2014
        To make that calculation useful, we first adjust the historical prices in our lookback windows. The price
        adjustment allows us to compare prices across splits and dividends. The adjusted price for May 15 is
        ($588.82/7), or $84.12. That enables us to calculate the percent change in AAPL from May 15, 2014 to
        August 1, 2014 to be 14.3%.
        """

        d0 = date(2014, 5, 15)
        d1 = date(2014, 8, 1)
        delta = d1 - d0  # delta.days

        self.data.set_sliding_window(lookback=delta.days)
        self.data.sliding_start_date = "2014-05-15"
        self.data.sliding_end_date = "2014-08-01"

        adjusted_data = self.data.get_adjusted_window(manual_window=True)
        close_price = adjusted_data['AAPL']

        # After adjustment, calculate the percent change in AAPL from May 15, 2014 to August 1, 2014 to be 14.3%
        pct_change = 100 * (close_price[-1] - close_price[0]) / close_price[0]
        self.assertTrue(14.2 < pct_change < 14.3)

    def test_sliding_window_adj_close(self):
        """
        This test represents the information provided by Quantopian on their lookback adjusted prices:
        Lookback windows now use prices that are split-, merger-, and dividend-adjusted.

        You can now make accurate calculations of the returns of securities because the price information in the
        lookback window is fully adjusted. When your algorithm calls for historical data using history() or in
        pipeline calculations, the data is returned to the algorithm with prices adjusted to the date of simulation.

        source: https://web.archive.org/web/20190215100332/https://www.quantopian.com/quantopian2/adjustments
        :return:
        """

        d0 = date(2014, 5, 15)
        d1 = date(2014, 8, 1)
        delta = d1 - d0  # delta.days

        self.data.set_sliding_window(lookback=delta.days)

        self.data.set_sliding_window(lookback=delta.days)
        self.data.sliding_start_date = "2014-05-15"
        self.data.sliding_end_date = "2014-08-01"

        adjusted_data = self.data.get_adjusted_window(manual_window=True)
        close_price = adjusted_data['AAPL']

        # May 15th Price
        self.assertEqual(round(close_price[0], 2), 84.12)
        # May 30th price
        self.assertEqual(round(close_price[pd.Timestamp('2014-05-30').tz_localize('America/New_York')]
                               , 2), 90.43)
        # June 6th price
        self.assertEqual(round(close_price[pd.Timestamp('2014-06-06').tz_localize('America/New_York')]
                               , 2), 92.22)
        # June 9th price
        self.assertEqual(round(close_price[pd.Timestamp('2014-06-09').tz_localize('America/New_York')]
                               , 2), 93.7)
        # June 13th price
        self.assertEqual(round(close_price[pd.Timestamp('2014-06-13').tz_localize('America/New_York')]
                               , 2), 91.28)


class TestingTradingDayOfMonth(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestingTradingDayOfMonth, self).__init__(*args, **kwargs)

    def test_from_last_day(self):
        today_date = '2023-10-31'
        today_date = pd.Timestamp(today_date)

        sliding_window = btadj.SlidingWindow(lookback=180)
        sliding_window.today = today_date
        sliding_window.set_end_date_as_last_trading_day_of_previous_month()
        self.assertEqual(sliding_window.sliding_end_date.strftime("%Y-%m-%d"),
                         datetime(2023, 9, 29).strftime("%Y-%m-%d"))
        self.assertEqual(sliding_window.first_trading_day_of_month.strftime("%Y-%m-%d"),
                         datetime(2023, 10, 2).strftime("%Y-%m-%d"))

    def test_from_first_day(self):
        today_date = '2023-11-01'
        today_date = pd.Timestamp(today_date)

        sliding_window = btadj.SlidingWindow(lookback=180)
        sliding_window.today = today_date
        sliding_window.set_end_date_as_last_trading_day_of_previous_month()
        self.assertEqual(sliding_window.sliding_end_date.strftime("%Y-%m-%d"),
                         datetime(2023, 10, 31).strftime("%Y-%m-%d"))

        self.assertEqual(sliding_window.first_trading_day_of_month.strftime("%Y-%m-%d"),
                         datetime(2023, 11, 1).strftime("%Y-%m-%d"))


class TestingNewYear2024(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestingNewYear2024, self).__init__(*args, **kwargs)

    def test_new_year(self):
        symbols = ['SPY']
        adj_window = btadj.DataBundle(assets_list=symbols)
        momentum_window = 180
        volatility_window = 20

        adj_window.set_sliding_window(lookback=max(momentum_window, volatility_window))

        d0 = datetime(2014, 1, 1).replace(hour=1, minute=1)
        current_time = d0.strftime("%Y-%m-%d")
        # valid trading day on which aaa must be determined
        today_date = '2024-1-1'
        target_date = pd.Timestamp(today_date)

        etf_df = adj_window.get_begining_of_month_adjusted_window(reference_datetime_date=target_date)
        self.assertEqual(adj_window.first_trading_day_of_month,
                         datetime(2024, 1, 2).date())

if __name__ == '__main__':
    unittest.main()
