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

import yfinance as yf  # alternative is yahoo_fin: https://theautomatic.net/yahoo_fin-documentation/
import pandas as pd
import os
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
import math
from pandas.tseries.offsets import BDay
import pytz
import sys


class ETFDataCorpActionFetcher:
    def __init__(self, ticker_symbol, store_csv=False, store_csv_dir="."):
        self.ticker_symbol = ticker_symbol
        self.ticker = None
        self.price_data = None
        self.dividends_data = None
        self.splits_data = None

        self.is_loaded_from_csv = False
        self.store_csv = store_csv
        self.store_csv_dir = store_csv_dir

    def download_data(self):
        print(f"\nthe Yahoo! finance API is intended for personal use only.")
        print(f"your use of this API means you have acknowledged and accepted Yahoo's terms of use available at "
              f"https://policies.yahoo.com/us/en/yahoo/terms/index.htm \n")

        self.ticker = yf.Ticker(self.ticker_symbol)

        # Download price data for all available years
        self.price_data = self.ticker.history(period="max", auto_adjust=False)

        # Download dividend data
        self.dividends_data = self.ticker.dividends

        # Download split data
        self.splits_data = self.ticker.splits

        print(f"\nStoring Yahoo CSV Files: {self.store_csv}")
        if self.store_csv:
            self.save_data_as_csv(folder_path=self.store_csv_dir)

    def load_and_process_csv(self, csv_file, timezone='America/New_York'):
        if not os.path.exists(csv_file):
            return None

        df = pd.read_csv(csv_file)

        # Validate Date Column
        if 'Date' not in df.columns:
            raise ValueError(f"Missing 'Date' column in {csv_file}")
            sys.exit(f"Clean Exit().")

        df.set_index('Date', inplace=True)

        # Convert index to DatetimeIndex
        try:
            df.index = pd.to_datetime(df.index, errors='coerce', utc=True)
        except Exception as e:
            raise ValueError(f"Error converting 'Date' to datetime in {csv_file}: {e}")
            sys.exit(f"Clean Exit().")

        # Check for NaN values in index
        if df.index.isna().any():
            raise ValueError(f"Invalid datetime values found in {csv_file}")
            sys.exit(f"Clean Exit().")

        # Ensure uniqueness
        if not df.index.is_unique:
            raise ValueError(f"Duplicate timestamps found in {csv_file}")
            sys.exit(f"Clean Exit().")

            # Handle timezone conversion
            original_tz = df.index.tz  # Capture original timezone if present
            if original_tz is None:
                df.index = df.index.tz_localize('UTC')
                raise Warning(" The data appears to be timezone-naive. We have enforced 'America/New_York' timezone. "
                              "Please make sure this is the correct timezone for your data.")
            else:
                # Check if original timezone is in North America
                valid_na_timezones = {tz for tz in pytz.all_timezones if tz.startswith("America/")}
                if original_tz.zone not in valid_na_timezones:
                    raise ValueError(
                        f"Timezone {original_tz} in {csv_file} is not a recognized North American timezone.")
                    sys.exit("Clean Exit().")

        # Convert from UTC to desired timezone
        df.index = df.index.tz_convert(pytz.timezone(timezone))

        # Normalize to midnight without DST adjustment risks
        df.index = df.index.normalize()

        # Ensure timezone is correctly applied without DST issues
        try:
            df.index = df.index.tz_localize(None).tz_localize(pytz.timezone(timezone), ambiguous='raise')
        except Exception as e:
            raise ValueError(f"Timezone localization issue in {csv_file}: {e}")
            sys.exit(f"Clean Exit().")

        # Convert to Series if single column
        if df.shape[1] == 1:
            df = df.squeeze(axis=1)

        return df

    def load_data_from_csv(self, csv_path):

        csv_file = os.path.join(csv_path, f'{self.ticker_symbol}.price.csv')
        self.price_data = self.load_and_process_csv(csv_file)

        csv_file = os.path.join(csv_path, f'{self.ticker_symbol}.dividends.csv')
        self.dividends_data = self.load_and_process_csv(csv_file)

        csv_file = os.path.join(csv_path, f'{self.ticker_symbol}.splits.csv')
        self.splits_data = self.load_and_process_csv(csv_file)

        self.is_loaded_from_csv = True
        self.store_csv = False

    def save_data_as_csv(self, folder_path="."):
        if self.is_loaded_from_csv or not self.store_csv:
            return

        if self.price_data is not None:
            print(f" >> saving {folder_path}/{self.ticker.ticker}.price.csv")
            self.price_data.to_csv(f"{folder_path}/{self.ticker.ticker}.price.csv")
        if self.dividends_data is not None:
            print(f" >> saving {folder_path}/{self.ticker.ticker}.dividends.csv")
            self.dividends_data.to_csv(f"{folder_path}/{self.ticker.ticker}.dividends.csv")
        if self.splits_data is not None:
            print(f" >> saving {folder_path}/{self.ticker.ticker}.splits.csv")
            self.splits_data.to_csv(f"{folder_path}/{self.ticker.ticker}.splits.csv")


class SlidingWindow:
    def __init__(self, lookback=None):
        self.lookback = lookback

        self.today = None
        self.sliding_start_date = None
        self.sliding_end_date = None
        self.first_trading_day_of_month = None

        self.calendar = mcal.get_calendar('XNYS')  # NYSE calendar

    def set_sliding_window(self, lookback):
        self.lookback = lookback

    def get_end_date(self):
        # replace the day with the first day of the month and shift the date one month back
        # then move to next business day (in case 1st is not a business day)
        previous_month = self.today.replace(day=1) - pd.DateOffset(months=1) + BDay(1)
        schedule = self.calendar.schedule(start_date=previous_month, end_date=self.today)
        # end of the window is the last trading day before today
        # today might not be a trading day, but also we may not want to get "last_month_last_trading" if provided
        # the date manually - thus the below structure
        self.sliding_end_date = schedule.iloc[-1]['market_open'].date()
        if self.sliding_end_date == self.today:
            self.sliding_end_date = schedule.iloc[-2]['market_open'].date()

    def set_end_date_as_last_trading_day_of_previous_month(self):
        # replace the day with the first day of the month and shift the date one month back
        # then move to next business day (in case 1st is not a business day)
        previous_month = self.today.replace(day=1) - pd.DateOffset(months=1) + BDay(1)

        # set the relevant first rebalancing date of the month from all trading days up to day 20 of months (or the
        # most recent trading day before that). The objective is to handle multiple scenarios of
        # "first trading days" and make sure it is in schedule.
        schedule = self.calendar.schedule(start_date=previous_month, end_date=self.today.replace(day=20))
        self.first_trading_day_of_month = schedule[schedule['market_open'].dt.month ==
                                                   self.today.month].iloc[0]['market_open'].date()

        schedule_filter_previous_only = schedule[schedule['market_open'].dt.month == previous_month.month]
        last_trading_day_of_previous_month = schedule_filter_previous_only.iloc[-1]['market_open'].date()
        # set both start and end dates
        self.sliding_end_date = last_trading_day_of_previous_month
        self.get_start_date()

    def get_start_date(self):
        # security: get 2x the fewest nb of trading days per month (16)
        # since the year 2000, 16 trading days in February 2009 was the fewest due to market holidays and weekends
        fewest_trading_day_month = 16
        # replace the day with the first day of the month and shift the date one month back
        # then move to next business day (in case 1st is not a business day)
        previous_month = (self.today.replace(day=1) -
                          pd.DateOffset(months=math.ceil(self.lookback/fewest_trading_day_month)) + BDay(1))
        schedule = self.calendar.schedule(start_date=previous_month, end_date=self.sliding_end_date)
        self.sliding_start_date = schedule.iloc[-self.lookback]['market_open'].date()


class History(SlidingWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.as_traded_prices = {}

    def unadjust_close_prices(self, asset):
        price_data = asset.price_data
        price_data = price_data.assign(RawClose='')
        price_data['RawClose'] = price_data['Close']

        splits_data = asset.splits_data
        # adjust for split ratio to get true historical price
        if splits_data is not None:
            for date, ratio in splits_data.sort_index(ascending=False).items():
                price_data.loc[price_data.index <= date, 'RawClose'] *= ratio

        self.as_traded_prices[asset.ticker_symbol] = pd.DataFrame(price_data['RawClose'])

    def adjust_prices_within_date_range(self, asset, today_date=None, manual_window=False, close_only=True):

        if not manual_window and self.today != today_date:
            self.today = today_date
            self.get_end_date()
            self.get_start_date()

        start_date = pd.Timestamp(self.sliding_start_date).tz_localize("America/New_York")
        end_date = pd.Timestamp(self.sliding_end_date).tz_localize("America/New_York")

        price_data = asset.price_data
        splits_data = asset.splits_data
        dividends_data = asset.dividends_data

        # window_data = price_data[(price_data.index >= start_date) & (price_data.index <= end_date)]
        window_data = pd.DataFrame(self.as_traded_prices[asset.ticker_symbol][(price_data.index >= start_date) &
                                                                              (price_data.index <= end_date)])
        window_data = window_data.rename(columns={'RawClose': 'AdjRaw'})

        # window_data = window_data.assign(AdjRaw='')
        # window_data['AdjRaw'] = window_data['RawClose']

        # if close_only:
        #    window_data = window_data.drop("Open", axis=1)
        #    window_data = window_data.drop("High", axis=1)
        #    window_data = window_data.drop("Low", axis=1)
        #    window_data = window_data.drop("Volume", axis=1)

        # Yahoo Close price ALREADY adjusted for splits
        for date, split in splits_data.items():
            # date = _date.tz_localize(None)
            if start_date <= date <= end_date:
                # Adjust close prices for splits - before split date
                window_data.loc[window_data.index <= date] /= split

        # Adjust close prices for dividends and splits within the time window
        for date, dividend in dividends_data.items():
            # date = _date.tz_localize(None)
            if start_date <= date <= end_date:
                # Adjust close prices for dividends - before split date (end_date is real current price)
                # For example, assume a company declared a $1 cash dividend and was trading at $51 per share before
                # then. All other things being equal, the stock price would fall to $50 because that $1 per share is
                # no longer part of the company's assets. However, the dividends are still part of the investor's
                # returns. By subtracting dividends from previous stock prices, we obtain the adjusted closing prices
                # and a better picture of returns.
                div_ratio = 1 - dividend / window_data.loc[date]
                window_data.loc[window_data.index <= date] *= div_ratio

        return window_data


class DataBundle(History):
    def __init__(self, assets_list, csv_path=None, **kwargs):
        self.assets_list = assets_list

        self.fetcher = {}
        for _asset in assets_list:
            self.fetcher[_asset] = ETFDataCorpActionFetcher(ticker_symbol=_asset)

        super().__init__(**kwargs)

        if csv_path is not None:
            for _asset in self.assets_list:
                self.fetcher[_asset].load_data_from_csv(csv_path=csv_path)
                self.unadjust_close_prices(asset=self.fetcher[_asset])
        else:
            for _asset in self.assets_list:
                self.fetcher[_asset].download_data()
                self.fetcher[_asset].save_data_as_csv()
                self.unadjust_close_prices(asset=self.fetcher[_asset])

    def check_nan_columns(self, etf_df):
        # Identify columns that are completely NaN
        full_nan_cols = etf_df.columns[etf_df.isna().all()].tolist()
        if full_nan_cols:
            raise ValueError(f"[data_adjuster/DataBundle/get_adjusted_window] "
                             f"Data inconsistency detected: The following columns are entirely NaN, "
                             f"which may be related to timezone-aware context issues: {full_nan_cols}")
            sys.exit(1)

        # Identify columns that have some NaN values but are not entirely NaN
        partial_nan_cols = etf_df.columns[etf_df.isna().any() & ~etf_df.isna().all()].tolist()
        if partial_nan_cols:
            start_time = etf_df.index.min()
            end_time = etf_df.index.max()
            raise ValueError(
                f"[data_adjuster/DataBundle/get_adjusted_window] Warning: The following columns contain some NaN values: {partial_nan_cols}\n"
                f"Please check input data appropriateness. Data time range: {start_time} to {end_time}")
            sys.exit(1)

    def get_adjusted_window(self, today_date=None, manual_window=False):
        if not manual_window:
            etf_df = pd.DataFrame()
            for key, value in self.fetcher.items():
                adjusted_data = self.adjust_prices_within_date_range(
                    asset=value,
                    today_date=today_date
                )
                etf_df[key] = pd.DataFrame(adjusted_data['AdjRaw'])
        else:
            etf_df = pd.DataFrame()
            for key, value in self.fetcher.items():
                adjusted_data = self.adjust_prices_within_date_range(
                    asset=value, manual_window=True)
                etf_df[key] = pd.DataFrame(adjusted_data['AdjRaw'])

        self.check_nan_columns(etf_df)
        return etf_df

    def get_begining_of_month_adjusted_window(self, reference_datetime_date=None):
        """
        get the time-adjusted window of prices for a given lookback window at the beginning of a month
        default: date.today()
        :param reference_datetime_date: datetime.date() format
        :return: dataframe of time-adjusted close price
        """
        if reference_datetime_date is None:
            self.today = date.today()
        else:
            self.today = reference_datetime_date
        self.set_end_date_as_last_trading_day_of_previous_month()
        return self.get_adjusted_window(manual_window=True)


# Example usage:
if __name__ == "__main__":
    import pathlib
    from datetime import date

    csv_path = pathlib.Path(__file__).parent
    assets_list = ["AAPL"]  # reproduce quantopian analysis

    data = DataBundle(assets_list=assets_list)

    d0 = date(2014, 5, 15)  # reproduce quantopian analysis
    d1 = date(2014, 8, 1)  # reproduce quantopian analysis
    delta = d1 - d0  # delta.days
    data.set_sliding_window(lookback=delta.days)

    data.sliding_start_date = "2014-05-15"
    data.sliding_end_date = "2014-08-01"

    adjusted_data = data.get_adjusted_window(manual_window=True)

    as_traded = data.as_traded_prices['AAPL']
    close_price = adjusted_data['AAPL']
    ydata = data.as_traded_prices['AAPL'].RawClose
    print(f" percent change: 14.3% > {100 * (close_price[-1] - close_price[0]) / close_price[0]}")
    print(f" May 15th price: 84.12 > {close_price[0]}")
    print(
        f" May 15th price: 588.82 > {as_traded['RawClose'][pd.Timestamp('2014-05-15').tz_localize('America/New_York')]}")
    print(
        f" May 30th price: 633 > {as_traded['RawClose'][pd.Timestamp('2014-05-30').tz_localize('America/New_York')]}")
    print(
        f" June 6th price: $645.57 > {as_traded['RawClose'][pd.Timestamp('2014-06-06').tz_localize('America/New_York')]}")
    print(
        f" June 9th price: 93.7 or 656 > {as_traded['RawClose'][pd.Timestamp('2014-06-09').tz_localize('America/New_York')]}")
    print(
        f" June 13th price: 91.28 > {as_traded['RawClose'][pd.Timestamp('2014-06-13').tz_localize('America/New_York')]}")

    print(
        f" Aug 31st 2020 price: 516.16 > {ydata[pd.Timestamp('2020-08-31').tz_localize('America/New_York')]}")
    print(
        f" 28 February 2005 price: $90 > {ydata[pd.Timestamp('2005-02-28').tz_localize('America/New_York')]}")
    print(
        f" 21 June 2000 price: $111 > {ydata[pd.Timestamp('2000-06-21').tz_localize('America/New_York')]}")
    print(
        f" 16 June 1987 price: $83 > {ydata[pd.Timestamp('1987-06-16').tz_localize('America/New_York')]}")

    print(f" AdjRaw for period {data.sliding_start_date}-{data.sliding_end_date} | May 15th price > {close_price[0]}")
    print(
        f" AdjRaw for period {data.sliding_start_date}-{data.sliding_end_date} | May 30th price 84.12 > {close_price[pd.Timestamp('2014-05-30').tz_localize('America/New_York')]}")
    print(
        f" AdjRaw for period {data.sliding_start_date}-{data.sliding_end_date} | June 6th price > {close_price[pd.Timestamp('2014-06-06').tz_localize('America/New_York')]}")
    print(
        f" AdjRaw for period {data.sliding_start_date}-{data.sliding_end_date} | June 9th price: 93.7 > {close_price[pd.Timestamp('2014-06-09').tz_localize('America/New_York')]}")
    print(
        f" AdjRaw for period {data.sliding_start_date}-{data.sliding_end_date} | June 13th price: 91.28 > {close_price[pd.Timestamp('2014-06-13').tz_localize('America/New_York')]}")

    print(f"\nGetting the adjusted close price (as df.head(5)) of the beginning of the current month - lookback value: {data.lookback}")
    print(data.get_begining_of_month_adjusted_window().head(5))

    print(f"\nGetting the adjusted close price (as df.head(5)) for {str(datetime(2023, 5, 8).date())}")
    print(data.get_begining_of_month_adjusted_window(
        reference_datetime_date=datetime(2023, 5, 8).date()).head(5))
