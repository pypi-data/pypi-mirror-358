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

import pandas as pd
import backtrader as bt
from backtrader_contrib.framework.lucid.data.data_adjuster import ETFDataCorpActionFetcher


class ImportHistoricalData(object):

    def __init__(self, start_date, end_date, time=9, tz='America/New_York',
                 store_yahoo_csv=False, data_dir="."):
        self.start_date = start_date
        self.end_date = end_date
        self.time = time
        self.tz = tz
        self.store_yahoo_csv = store_yahoo_csv
        self.data_dir = data_dir
        return

    def custom_csv(self, file):
        ###############################################################################
        # DATA FORMAT: .csv                                                           #
        # date	        close	    volume	Open	    high	low        Adj Close  #                 #
        # 2000-12-28	92.889801	8358700	132.8125	133.875	132.59375   123.45    #
        ###############################################################################

        # Simulate the header row isn't there if noheaders requested
        skiprows = 0
        header = 0
        dataframe = None

        try:
            dataframe = pd.read_csv(file,
                                    skiprows=skiprows,
                                    header=header,
                                    parse_dates=True,
                                    index_col=0
                                    )
        except IOError:
            print('\n ----------------------- \n CANNOT OPEN ASSET FILE \n ----------------------- \n', file)
            print('\n')
            exit(-1)

        return self.df_to_btfeed(dataframe)

    def historical_yahoo(self, equity, csv_fmt=False):
        print(f"\nthe Yahoo! finance API is intended for personal use only.")
        print(f"your use of this API means you have acknowledged and accepted Yahoo's terms of use available at "
              f"https://policies.yahoo.com/us/en/yahoo/terms/index.htm \n")
        #yf.pdr_override()
        #df = pdr.get_data_yahoo(equity, start=self.start_date, end=self.end_date)
        #df = df.drop("Close", axis=1)

        yf_datafeed = ETFDataCorpActionFetcher(ticker_symbol=equity, store_csv=self.store_yahoo_csv,
                                               store_csv_dir=self.data_dir)
        yf_datafeed.download_data()
        columns_to_keep = ['Open', 'High', 'Low', 'Adj Close', 'Volume']
        df = yf_datafeed.price_data[columns_to_keep]

        df.rename(columns={'Adj Close': 'close', 'Volume': 'volume', 'Low': 'low', 'High': 'high', 'Open': 'open'},
                  inplace=True)
        df.index.rename('date', inplace=True)

        if csv_fmt:
            return df
        else:
            # to be ingested by bt as a btfeed
            return self.df_to_btfeed(df)

    def df_to_btfeed(self, dataframe):

        # Ensure the index is a DatetimeIndex
        dataframe.index = pd.to_datetime(dataframe.index)
        # Set time to 09:00:00 for each date
        dataframe.index = dataframe.index.normalize() + pd.Timedelta(hours=9)

        if dataframe.index.tz is None:
            dataframe.index = dataframe.index.tz_localize(self.tz)
        else:
            dataframe.index = dataframe.index.tz_convert(self.tz)

        """
        # creating a new index with starting time at 9am
        temp = []
        for i in range(0, len(dataframe.index)):
            temp.append(dataframe.index[i] + pd.DateOffset(hours=9))

        # adding the new index in the df, and switching to new index
        dataframe['nysetime'] = pd.Series(temp, index=dataframe.index)
        dataframe.set_index('nysetime', inplace=True)
        #dataframe = dataframe.tz_localize(self.tz)
        dataframe = dataframe.index.tz_convert(self.tz)
        """

        # reoredering the df chronologically
        data = dataframe.sort_index(ascending=True)

        if self.start_date is not None and self.end_date is not None:
            data = data.loc[self.start_date:self.end_date]
        elif self.start_date is not None:
            data = data.loc[self.start_date:]
        elif self.end_date is not None:
            data = data.loc[:self.end_date]
        # data = dataframe.reindex(index=temp[::-1])
        return bt.feeds.PandasData(dataname=data)
