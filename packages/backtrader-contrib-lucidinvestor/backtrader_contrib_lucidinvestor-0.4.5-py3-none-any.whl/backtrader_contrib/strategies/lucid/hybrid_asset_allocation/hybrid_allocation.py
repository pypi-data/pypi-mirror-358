from backtrader_contrib.framework.lucid.utils.allocator_base import LucidAllocatorBase
import pandas as pd


class HybridAllocation(LucidAllocatorBase):
    """
    US Equities (SPY, IWM), Foreign Equities (VEA, VWO), Alternative Assets (VNQ, DBC) and US Treasury Bonds (IEF, TLT)
    """
    params = LucidAllocatorBase.params + (
        ('lookback_window', 252),  # 1-year lookback
        ('offensive_assets', ["SPY", "IWM", "VEA", "VWO", "VNQ", "DBC", "IEF", "TLT"]),
        ('cash_proxy', "BIL"),  # US T-Bills as cash proxy
        ('canary', "TIP"),  # Canary asset
        ('offensive_trade', False),
        ('fast_mom', False),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.offensive_symbols = {
            'SPY': "SSO",
            'IWM': "UWM",
            'QQQ': "QLD",
            'VNQ': 'URE',
            'TLT': 'UBT',
            'IEF': 'UST'
        }

    def set_lookback_window(self):
        """ Ensure we have enough historical data for 1, 3, 6, and 12-month returns """
        return self.p.lookback_window

    def calculate_momentum(self, df, weighted=True):
        """
        Calculate the momentum for each asset using either weighted (13612W) or unweighted average of 1, 3, 6, and 12-month % returns.

        weighted refers to the 13612W, aka fast momentum:
        https://alphaarchitect.com/2018/12/trend-following-on-steroids/

        Parameters:
        df (pd.DataFrame): A DataFrame with dates as the index and asset prices as columns.
        weighted (bool): If True, applies 13612W weighting; otherwise, uses an unweighted average.

        Returns:
        pd.Series: A Series containing the momentum score for each asset.
        """
        # Ensure DataFrame is sorted by date (ascending order)
        df = df.sort_index()

        # Compute momentum returns
        returns_1m = (df.iloc[-1] - df.iloc[-21]) / df.iloc[-21]  # 1-month return (21 trading days)
        returns_3m = (df.iloc[-1] - df.iloc[-63]) / df.iloc[-63]  # 3-month return (63 trading days)
        returns_6m = (df.iloc[-1] - df.iloc[-126]) / df.iloc[-126]  # 6-month return (126 trading days)
        returns_12m = (df.iloc[-1] - df.iloc[0]) / df.iloc[0]  # 12-month return (252 trading days)

        # Combine into a DataFrame
        combined_returns = pd.DataFrame({
            '1m': returns_1m,
            '3m': returns_3m,
            '6m': returns_6m,
            '12m': returns_12m
        })

        if weighted:
            # Apply 13612W weighting
            weights = [12, 4, 2, 1]
            momentum = (combined_returns * weights).sum(axis=1) / sum(weights)
        else:
            # Unweighted mean
            momentum = combined_returns.mean(axis=1)

        return momentum

    def switch_to_offensive(self, weights):
        """
        source: https://indexswingtrader.blogspot.com/2018/12/exploring-smart-leverage-daa-on-steroids.html

        the smart leverage approach incorporates a clever separation of signals and trades. As proposed by Matthias
        Koch, a quant from Germany, non-leveraged asset universes are used for signaling momentum based position
        sizing while universes that hold a limited number of matching leveraged funds are used for actual trading.

        When the stock market is in an uptrend - positive 13612W momentum for all canary assets -
        favorable conditions for leveraged stock positions are assumed targeting positive streaks in performance.
        When the stock market is in a downtrend - negative 13612W momentum for one or more of the canary assets -
        a rise in volatility is expected and a (relatively) safe Treasury bond position is acquired to avoid the
        constant leverage trap for stocks.

        Parameters:
        weights (dict): A dictionary containing asset symbols as keys and their weights as values.

        Returns:
        dict: A new dictionary with offensive symbols replaced.
        """
        offensive_weights = {}

        for symbol, weight in weights.items():
            # If the symbol exists in offensive_symbols, replace it with its offensive counterpart
            if symbol in self.offensive_symbols:
                offensive_weights[self.offensive_symbols[symbol]] = weight
            else:
                offensive_weights[symbol] = weight

        return offensive_weights

    def assign_equal_weight(self, today_date):

        etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)

        # Calculate the momentum of each asset in the (risky) offensive, defensive (BIL/IEF) and canary (TIP)
        # universe, where momentum is the average total return over the past 1, 3, 6, and 12 months.
        momentum_scores = self.calculate_momentum(etf_df, weighted=self.p.fast_mom)
        # Extract specific asset momentums
        risky_momentum = momentum_scores.get(self.p.offensive_assets)
        tips_momentum = momentum_scores.get(self.p.canary)
        cash_momentum = momentum_scores.get(self.p.cash_proxy)

        # allocate 1/TopX (equally weighted)
        eq_weight = 1 / float(self.p.nb_asset_in_portfolio)
        if tips_momentum > 0:
            # select the best TopX half of the risky assets
            top_assets = risky_momentum.nlargest(self.p.nb_asset_in_portfolio).index.tolist()
            weights = {}

            for asset in top_assets:
                # replacing each of those TopX assets by the best ‘cash’ asset when ‘bad’
                # (i.e. has non-positive momentum)
                if risky_momentum[asset] > 0:
                    weights[asset] = eq_weight  # Assign 25% if positive momentum
                else:
                    defensive_asset = cash_momentum.nlargest(1).index.tolist()[0]
                    weights[defensive_asset] = eq_weight  # Otherwise, allocate to cash/IEF
        else:
            # Defensive mode: Select only the best defensive ‘cash’ asset (BIL or IEF) when TIP is bad
            defensive_asset = cash_momentum.nlargest(1).index.tolist()[0]
            weights = {defensive_asset: 1.0}

        if self.p.offensive_trade:
            weights = self.switch_to_offensive(weights)
        return weights
