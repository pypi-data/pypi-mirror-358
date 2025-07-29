import pandas as pd
from arch import arch_model
from backtrader_contrib.framework.lucid.utils.allocator_base import LucidAllocatorBase


class SectorRotationGiordano(LucidAllocatorBase):
    """
    Antifragile Asset Allocation (AAA) Strategy

    The AAA strategy dynamically allocates assets to a portfolio based on a ranking system that integrates four key factors:
    - **Absolute Momentum (M)**: Measures the profitability of assets over a specific lookback period (default: 4 months).
    - **Volatility (V)**: Measures the risk of assets using a GARCH(1,1) model, which provides dynamic volatility estimates.
    - **Average Relative Correlation (C)**: Measures diversification by calculating the average correlation across the assets, ensuring the portfolio isn’t overly correlated.
    - **ATR Trend/Breakout System (T)**: Measures the directionality of price movements using Average True Range (ATR) bands, helping to identify breakout or breakdown events.

    **Portfolio Construction and Hedging**:
    - The strategy ranks assets based on a combined score, TRank, which is calculated by weighting the four factors above.
    - **Top 5 ETFs**: The strategy selects the top 5 ETFs by TRank score and allocates them proportionally.

    Parameters:
    -----------
    momentum_window : int
        Lookback period for calculating Absolute Momentum (default: 84 days, ~4 months).
    volatility_window : int
        Lookback period for calculating Volatility (default: 84 days).
    correlation_window : int
        Lookback period for calculating Average Relative Correlation (default: 84 days).
    atr_window : int
        Lookback period for calculating ATR (default: 42 days).
    high_period : int
        Lookback period for the highest close in ATR bands (default: 63 days).
    low_period : int
        Lookback period for the lowest close in ATR bands (default: 105 days).
    nb_asset_in_portfolio : int
        Number of top ETFs to include in the portfolio (default: 3).
    hedge_asset : str
        Asset to use as Cash (default: 'SHY').
    momentum_weight : float
        Weight for Absolute Momentum in TRank calculation (default: 0.4).
    volatility_weight : float
        Weight for Volatility in TRank calculation (default: 0.2).
    correlation_weight : float
        Weight for Correlation in TRank calculation (default: 0.2).
    atr_weight : float
        Weight for ATR Trend in TRank calculation (default: 0.2).
    """
    params = LucidAllocatorBase.params + (
        ('assets', ['XLY', 'XLP', 'XLE', 'XLF', 'XLV', 'XLI', 'XLB', 'XLK', 'XLU', 'VOX', 'RWR']),
        ('hedge', ['FXY', 'FXF', 'GLD', 'IEF', 'SH', 'TLT', 'SHY']),
        ('hedge_asset', 'SHY'),
        ('nb_asset', 0),
        ('momentum_window', 84),
        ('volatility_window', 84),
        ('correlation_window', 84),
        ('atr_window', 42),
        ('high_period', 63),
        ('low_period', 105),
        ('momentum_weight', 1),
        ('volatility_weight', 1),
        ('correlation_weight', 1),
        ('atr_weight', 1),  # todo: OHLC
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_lookback_window(self):
        return max(self.p.momentum_window, self.p.volatility_window, self.p.correlation_window, self.p.atr_window,
                   self.p.high_period, self.p.low_period)

    def absolute_momentum(self, df):
        """
        (M) Absolute Momentum: to determine assets’ profitability. (ROC – Rate of Change)
        Args:
            df:

        Returns:
            Rank from Most (1) to Least (11) trending

        """
        df_subset = df.iloc[-self.p.momentum_window:]
        return df_subset.iloc[-1] / df_subset.iloc[0]

    def sma_total_return(self, df):
        """
        Computes the Simple Moving Average (SMA) Total Return over the lookback window.

        Args:
            df: DataFrame containing daily prices for the lookback window.

        Returns:
            Series with SMA Total Return for each asset.
        """
        sma = df.mean()  # Compute the SMA over the lookback window
        total_return = df.iloc[-1] / sma  # Compute total return as last price / SMA
        return total_return

    def compute_volatility(self, df):
        """

        Args:
            df:

        Returns:
            Rank from least (1) to most (11) volatile
        """

        df_subset = df.iloc[-self.p.volatility_window:]
        # Calculate daily volatility (standard deviation of returns)
        returns = df_subset.pct_change().dropna()
        daily_volatility = returns.std()
        # Annualize the volatility (multiply by √252 for trading days in a year)
        annualized_volatility = daily_volatility * (252 ** 0.5)

        # Create a Series and rank in descending order (higher rank = more volatile)
        return pd.Series(annualized_volatility)

    def compute_garch_volatility(self, df, p=1, q=1, annualize=True, forecast_horizon=21):
        """
        (V) Volatility Model: Edited GARCH Model to estimate future asset risk.

        Args:
            df (DataFrame): Asset price data.
            p (int): Number of lags for the ARCH term.
            q (int): Number of lags for the GARCH term.
            annualize (bool): Whether to return annualized volatility.
            forecast_horizon (int): Days to forecast (e.g., 21 for ~1 month).

        Returns:
            Series: Ranked future GARCH volatility (higher rank = more volatile).
        """
        df_subset = df.iloc[-self.p.volatility_window:]
        returns = df_subset.pct_change().dropna()
        future_volatility = {}

        for asset in returns.columns:
            try:
                # Fit GARCH(p, q) model
                garch = arch_model(returns[asset], vol='Garch', p=p, q=q)
                res = garch.fit(disp='off')

                # Forecast future volatility for the given horizon
                forecasts = res.forecast(start=len(returns), horizon=forecast_horizon)

                # Get the mean predicted variance over the forecast horizon
                future_variance = forecasts.variance.mean().iloc[-1]

                # Convert to volatility (square root of variance)
                future_vol = future_variance ** 0.5

                # Annualize volatility if needed (assume 252 trading days/year)
                if annualize:
                    future_vol *= (252 ** 0.5)

                future_volatility[asset] = future_vol

            except Exception as e:
                print(f"Error processing {asset}: {e}")
                future_volatility[asset] = None

        # Create a Series and rank in descending order (higher rank = more volatile)
        volatility_series = pd.Series(future_volatility)
        return volatility_series.rank(ascending=True, method='min')

    def compute_avg_correlation(self, df):
        """
        (C) Average Relative Correlations: to achieve diversification. Calculation: 4 months average
        correlation across the ETFs

        Args:
            df:

        Returns:
            Rank from least (1) to most (11) correlated
        """
        # Limit to the desired correlation window
        df_subset = df.iloc[-self.p.correlation_window:]
        # Compute daily returns
        returns = df_subset.pct_change().dropna()

        # Compute correlation matrix
        corr_matrix = returns.corr()
        # Average correlation for each ETF (excluding self-correlation)
        return corr_matrix.mean().dropna()

    def compute_atr_trend(self, df):
        """
        (T) ATR Trend/Breakout System: to determine assets’ directionality. Calculation: ATR Bands on daily timeframe.
        Upper Band = 42 periods ATR + Highest Close of 63 periods. Lower Band = 42 periods ATR + Highest Low of
        105 periods.

        Args:
            df:

        Returns:

        """
        atr_trend_today = {}
        lookback_window = max(self.p.atr_window, self.p.low_period, self.p.high_period)
        df_subset = df.iloc[-lookback_window:]

        for asset in df.columns:
            try:
                true_range = df_subset[asset].rolling(self.p.atr_window).max() - df_subset[asset].rolling(
                    self.p.atr_window).min()
                atr = true_range.rolling(self.p.atr_window, min_periods=self.p.atr_window).mean()
                highest_close_63 = df_subset[asset].rolling(self.p.high_period, min_periods=self.p.high_period).max()
                upper_band = highest_close_63 + atr
                highest_low_105 = df_subset[asset].rolling(self.p.low_period, min_periods=self.p.low_period).max()
                lower_band = highest_low_105 - atr
                atr_trend_today[asset] = ((df_subset[asset].iloc[-1] > upper_band.iloc[-1]).astype(int) -
                                          (df_subset[asset].iloc[-1] < lower_band.iloc[-1]).astype(int))
            except:
                atr_trend_today[asset] = None

        return pd.Series(atr_trend_today)

    def compute_trank(self, df):
        """
        𝑇𝑅𝐴𝑁𝐾 = (𝑤𝑀 ∗ 𝑅𝑎𝑛𝑘(𝑀) + 𝑤𝑉 ∗ 𝑅𝑎𝑛𝑘(𝑉) + 𝑤𝐶 ∗ 𝑅𝑎𝑛𝑘(𝐶) − 𝑤𝑇 ∗ 𝑇) + 𝑀/𝑛

        Args:
            df:

        Returns:
            Rank from most (1) to least (11) optimal antifragile asset
        """

        # Rank from Most (1) to Least (11) trending
        momentum_df = self.absolute_momentum(df)
        sma_ret = self.sma_total_return(df)
        # only assets whose total return is above its simple moving average total return
        # https://info.recipeinvesting.com/recipe/t.srrs.html
        filtered_df = df.loc[:, momentum_df >= sma_ret]

        momentum_df = self.absolute_momentum(filtered_df)
        rank_M = momentum_df.rank(ascending=False, method='min')

        # Rank from least (1) to most (11) volatile
        #volatility_df = self.compute_garch_volatility(df)
        volatility_df = self.compute_volatility(filtered_df)
        rank_V = volatility_df.rank(ascending=True, method='min')

        # Rank from least (1) to most (11) correlated
        correlation_df = self.compute_avg_correlation(filtered_df)
        rank_C = correlation_df.rank(ascending=True, method='min')

        #atr_df = self.compute_atr_trend(df)

        trank = (
                self.p.momentum_weight * rank_M
                + self.p.volatility_weight * rank_V
                + self.p.correlation_weight * rank_C
                # - self.p.atr_weight * atr_df
                + momentum_df / self.p.nb_asset
        )

        return trank.rank(ascending=True, method='min')

    def assign_equal_weight(self, today_date):
        etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)

        trank_asset = self.compute_trank(etf_df.get(self.p.assets))

        if len(self.p.hedge) > 0:
            trank_hedge = self.compute_trank(etf_df.get(self.p.hedge))
            top_hedge = trank_hedge.nsmallest(3).index.tolist()
            # Filter out only those ETFs from top_hedge that have positive momentum
            momentum_df = self.absolute_momentum(etf_df.get(top_hedge))
            positive_momentum_hedge = [etf for etf in top_hedge if momentum_df[etf] > 0]

        top_etfs = trank_asset.nsmallest(self.p.nb_asset_in_portfolio).index.tolist()
        # Filter out only those ETFs from top_hedge that have positive momentum
        momentum_df = self.absolute_momentum(etf_df.get(top_etfs))
        positive_momentum_asset = [etf for etf in top_etfs if momentum_df[etf] > 0]

        portf_asset = top_etfs

        # If no positive momentum assets, use positive_momentum_hedge
        #if len(positive_momentum_asset) == 0:
        #    portf_asset = positive_momentum_hedge

        #else:
        #    # Replace ETFs in top_etfs that are not in positive_momentum_asset with the first ETF in positive_momentum_hedge
        #    for i in range(len(top_etfs)):
        #        if top_etfs[i] not in positive_momentum_asset:
        #            top_etfs[i] = positive_momentum_hedge[0]
        #
        #    portf_asset = top_etfs


        if False and len(positive_momentum_asset) > 0:

            portf = positive_momentum_asset
            to_fill = self.p.nb_asset_in_portfolio - len(portf)

            n_hedge = len(positive_momentum_hedge)
            for i in range(to_fill-1):
                if n_hedge > 0:
                    portf.append(positive_momentum_hedge[0])
                else:
                    portf.append(self.p.hedge_asset)

            equal_weight = 1.0 / len(portf)

            # Initialize an empty dictionary to hold the cumulative weights
            allocation = {}
            # Loop through the ETFs in portf and add the weights
            for etf in portf:
                # If the ETF is already in the allocation, add the new weight to its existing weight
                if etf in allocation:
                    allocation[etf] += equal_weight
                else:
                    # Otherwise, set the weight for the ETF
                    allocation[etf] = equal_weight

            return allocation
        elif len(top_etfs) > 0:
            equal_weight = 1.0 / len(top_etfs)
            return {etf:equal_weight for etf in top_etfs}
        else:
            return {self.p.hedge_asset: 1}
