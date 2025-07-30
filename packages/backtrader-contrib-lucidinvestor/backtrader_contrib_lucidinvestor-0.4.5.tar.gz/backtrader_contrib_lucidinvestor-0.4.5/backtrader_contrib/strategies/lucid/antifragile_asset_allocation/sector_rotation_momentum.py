from backtrader_contrib.framework.lucid.utils.allocator_base import LucidAllocatorBase
import pandas as pd


class SectorRotationMomentum(LucidAllocatorBase):
    """
    Sector rotation strategy based on TRank (momentum ranking).
    Inherits from LucidAllocatorBase to ensure consistency in allocation handling.
    """
    params = LucidAllocatorBase.params + (
        ('lookback_3m', 63),
        ('lookback_6m', 126),
        ('lookback_12m', 252)
    )

    def __init__(self, **kwargs):
        """
        Initializes SectorRotationMomentum with lookback periods.

        Args:
            lookback_3m (int): 3-month lookback window.
            lookback_6m (int): 6-month lookback window.
            lookback_12m (int): 12-month lookback window.
            kwargs: Additional parameters to pass to LucidAllocatorBase.
        """
        super().__init__(**kwargs)

    def set_lookback_window(self):
        """
        Defines the lookback window based on the longest period used in TRank computation.
        """
        return self.p.lookback_12m

    def compute_trank(self, df):
        """
        Computes TRank based on the sum of 3-month, 6-month, and 12-month returns.

        Args:
            df (pd.DataFrame): DataFrame containing asset prices.

        Returns:
            pd.Series: Ranked assets based on total returns.
        """
        returns_3m = df.pct_change(periods=self.p.lookback_3m).iloc[-1]
        returns_6m = df.pct_change(periods=self.p.lookback_6m).iloc[-1]
        returns_12m = df.pct_change(periods=self.p.lookback_12m).iloc[-1]

        total_returns = returns_3m + returns_6m + returns_12m
        return total_returns.rank(ascending=False, method='min')

    def assign_equal_weight(self, today_date):
        """
        Selects top ETFs based on TRank and assigns equal weights.

        Args:
            df (pd.DataFrame): DataFrame containing asset prices.

        Returns:
            dict: Dictionary with selected ETFs and their equal weights.
        """
        etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)

        trank = self.compute_trank(etf_df)
        top_etfs = trank.nsmallest(self.p.nb_asset_in_portfolio).index.tolist()
        equal_weight = 1.0 / len(top_etfs) if top_etfs else 0  # Handle empty selection case

        return {etf: equal_weight for etf in top_etfs}


class SectorRotationMomentumTopn(LucidAllocatorBase):
    """
    Sector rotation strategy implementing Top n Sector Rotation with cash allocation rule.
    This Portfolio Recipe sells an asset when it falls out of Top n ranking.

    mitigate downside risk during prolonged market downturns:
    If the S&P 500 (SPY) is below its 10-month simple moving average (SMA), the portfolio will allocate 100% to
    TLT (iShares 20+ Year Treasury Bond ETF) as a proxy for cash. Otherwise, the portfolio will follow its
    standard allocation strategy.
    """
    params = LucidAllocatorBase.params + (
        ('lookback_3m', 63),
        ('lookback_6m', 126),
        ('lookback_12m', 252),
        ('sma_10m', 210)  # 10-month SMA period (approx. 210 trading days)
    )

    def __init__(self, **kwargs):
        """Initializes SectorRotationMomentum with lookback periods."""
        super().__init__(**kwargs)
        self.current_holdings = set()

    def set_lookback_window(self):
        """Defines the lookback window based on the longest period used in TRank computation."""
        return max(self.p.lookback_12m, self.p.sma_10m)

    def compute_trank(self, df):
        """
        Computes TRank based on the sum of 3-month, 6-month, and 12-month returns.
        """
        returns_3m = df.pct_change(periods=self.p.lookback_3m).iloc[-1]
        returns_6m = df.pct_change(periods=self.p.lookback_6m).iloc[-1]
        returns_12m = df.pct_change(periods=self.p.lookback_12m).iloc[-1]

        total_returns = returns_3m + returns_6m + returns_12m
        return total_returns.rank(ascending=False, method='min')

    def is_below_sma(self, df):
        """
        Checks if SPY is below its 10-month simple moving average.
        """
        return df.iloc[-1] < df.rolling(self.p.sma_10m).mean().iloc[-1]

    def assign_equal_weight(self, today_date):
        """
        1. Selects top n ETFs based on TRank while preserving existing holdings if still in Top n.
        2. Allocates to an ETF only if it is above its 10-month SMA; otherwise, allocates to TLT.
        3. If SPY is below its 10-month SMA, allocate 100% to TLT.
        """
        etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)

        # Check if SPY is below its 10-month SMA
        if self.is_below_sma(etf_df)['SPY']:
            return {'TLT': 1.0}  # Move to cash equivalent (TLT)

        # Compute TRank and select top 3 ETFs
        # Exclude Canary
        asset_df = etf_df.drop(columns=['SPY', 'TLT'], errors='ignore')
        trank = self.compute_trank(asset_df)

        # top_3_etfs = set(trank.nsmallest(3).index.tolist())
        # top_3_etfs = set(trank.nsmallest(6).index.tolist()[3:6])
        top_n_etfs = set(trank.nlargest(self.p.nb_asset_in_portfolio).index.tolist())
        # top_3_etfs = set(trank.nlargest(6).index.tolist()[3:6])

        # # Retain ETFs from current holdings if still in Top n
        # selected_etfs = self.current_holdings.intersection(top_n_etfs)
        #
        # # Fill remaining spots with highest-ranked ETFs
        # new_etfs = list(top_n_etfs - selected_etfs)
        # selected_etfs.update(new_etfs[:self.p.nb_asset_in_portfolio - len(selected_etfs)])

        # Retain ETFs from current holdings if still in Top n and
        # its 10-month total return is above its 10-month SMA total return
        retained_etfs = set()
        for etf in self.current_holdings.intersection(top_n_etfs):
            etf_prices = etf_df[etf].dropna()
            if len(etf_prices) >= self.p.sma_10m:
                sma_10m_series = etf_prices.rolling(self.p.sma_10m).mean()
                total_return_10m = etf_prices.iloc[-1] / etf_prices.iloc[-self.p.sma_10m] - 1
                sma_total_return_10m = sma_10m_series.iloc[-1] / sma_10m_series.iloc[-self.p.sma_10m] - 1
                if total_return_10m > sma_total_return_10m:
                    retained_etfs.add(etf)

        selected_etfs = retained_etfs
        new_etfs = list(top_n_etfs - selected_etfs)
        selected_etfs.update(new_etfs[:3 - len(selected_etfs)])

        # Check if each selected ETF is above its 10-month SMA
        final_allocation = {}
        for etf in selected_etfs:
            etf_prices = etf_df[etf].dropna()
            if len(etf_prices) >= self.p.sma_10m:
                sma_10m = etf_prices.rolling(self.p.sma_10m).mean().iloc[-1]
                if etf_prices.iloc[-1] > sma_10m:
                    final_allocation[etf] = 1.0 / len(selected_etfs)
                else:
                    final_allocation['TLT'] = final_allocation.get('TLT', 0) + (1.0 / len(selected_etfs))
            else:
                # Not enough data for SMA, allocate to TLT
                final_allocation['TLT'] = final_allocation.get('TLT', 0) + (1.0 / len(selected_etfs))

        # Update current holdings
        self.current_holdings = set(final_allocation.keys())

        return final_allocation


class AntiFragileSectorRotationMomentum(LucidAllocatorBase):
    """
    Sector rotation strategy with antifragile approach based on TRank (momentum ranking).
    Replaces low momentum assets with hedging assets.
    Inherits from LucidAllocatorBase to ensure consistency in allocation handling.
    """
    params = LucidAllocatorBase.params + (
        ('lookback_3m', 63),
        ('lookback_6m', 126),
        ('lookback_12m', 252),
        ('sma_10m', 210),
        ('momentum_4m', 84),  # 4-month momentum (ROC)
    )

    # List of hedging assets
    hedging = ['FXY', 'FXF', 'GLD', 'IEF', 'SH', 'TLT', 'SHY']

    def __init__(self, **kwargs):
        """
        Initializes SectorRotationMomentum with lookback periods.
        """
        super().__init__(**kwargs)
        self.current_holdings = set()

    def is_below_sma(self, df):
        """
        Checks if SPY is below its 10-month simple moving average.
        """
        return df.iloc[-1] < df.rolling(self.p.sma_10m).mean().iloc[-1]

    def set_lookback_window(self):
        """
        Defines the lookback window based on the longest period used in TRank computation.
        """
        return self.p.lookback_12m

    def compute_trank(self, df):
        """
        Computes TRank based on the sum of 3-month, 6-month, and 12-month returns.
        """
        returns_3m = df.pct_change(periods=self.p.lookback_3m).iloc[-1]
        returns_6m = df.pct_change(periods=self.p.lookback_6m).iloc[-1]
        returns_12m = df.pct_change(periods=self.p.lookback_12m).iloc[-1]

        total_returns = returns_3m + returns_6m + returns_12m
        return total_returns.rank(ascending=False, method='min')

    def compute_absolute_momentum(self, df):
        df_subset = df.iloc[-self.p.momentum_4m:]
        momentum_values = (df_subset.iloc[-1] / df_subset.iloc[0] - 1) * 100
        return momentum_values.rank(ascending=False, method='min')

    def assign_equal_weight(self, today_date):
        """
        Selects top 3 ETFs based on TRank and assigns equal weights.
        Replaces assets with negative momentum by the best 3 hedging assets.
        """
        etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)

        # Compute TRank for all assets
        non_hedging_df = etf_df.drop(columns=self.hedging, errors='ignore')
        trank = self.compute_trank(non_hedging_df)
        top_etfs = trank.nlargest(self.p.nb_asset_in_portfolio).index.tolist()

        # Determine top 3 hedging assets based on TRank
        hedging_df = etf_df[self.hedging]
        hedging_trank = self.compute_trank(hedging_df)
        top_hedging_etfs = hedging_trank.nlargest(self.p.nb_asset_in_portfolio).index.tolist()

        selected_etfs = []

        if self.is_below_sma(etf_df)['SPY']:
            return {'TLT': 1.0}
            #return {top_hedging_etfs[0]: 1.0}  # Move to cash equivalent (TLT)
            #selected_etfs = top_hedging_etfs
        else:
            # Check momentum for each top ETF and replace with hedging asset if necessary
            momentum = self.compute_absolute_momentum(etf_df)
            for etf in top_etfs:
                #if momentum[etf] < 0:
                if self.is_below_sma(etf_df)[etf]:
                    # Replace with the first available hedging ETF
                    #selected_etfs.append(top_hedging_etfs.pop(0))
                    selected_etfs.append('TLT')
                else:
                    selected_etfs.append(etf)

        self.current_holdings = selected_etfs  # Update holdings

        # Assign equal weight to each selected ETF
        equal_weight = 1.0 / len(selected_etfs) if selected_etfs else 0
        return {etf: equal_weight for etf in selected_etfs}
