from backtrader_contrib.framework.lucid.utils.allocator_base import LucidAllocatorBase
import numpy as np


class UISAllocation(LucidAllocatorBase):
    """
    Universal Investment Strategy (UIS) that dynamically allocates between SPY and TLT
    using a modified Sharpe ratio approach.
    
    volatility_factor:  default is 5/2. To put it into perspective, at a power of 1, this is the basic Sharpe ratio,
                        and at a power of 0, just a momentum maximization algorithm.
    """

    params = LucidAllocatorBase.params + (
        ('lookback_window', 72),  # 72-day lookback period
        ('volatility_factor', 5/2),  # Factor in modified Sharpe ratio
        ('assets', ["SPY", "TLT"]),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_lookback_window(self):
        """ Ensure we have enough historical data for Sharpe ratio calculations. """
        return self.p.lookback_window

    def modified_sharpe_ratio(self, df):
        """
        Compute the modified Sharpe ratio for each possible allocation ratio of SPY/TLT.

        Args:
            df (DataFrame): Adjusted price data for SPY and TLT over the lookback period.

        Returns:
            float: The best allocation ratio (SPY weight).
        """
        period = self.p.lookback_window

        # Compute daily returns
        returns = df.pct_change().dropna()

        # Compute 72-day cumulative return (compounded return over lookback period)
        cum_return = (df.iloc[-1] / df.iloc[0]) ** (252 / period) - 1  # Annualized return

        # Compute standard deviation over the 72-day period, then annualize
        std_dev = returns.std() * np.sqrt(252)

        best_sharpe = -np.inf
        best_allocation = 0.0

        # Iterate through different SPY/TLT allocations (0% to 100% SPY in 5% increments)
        for weight_spy in np.linspace(0, 1, 21):
            weight_tlt = 1 - weight_spy

            # Portfolio return and standard deviation using weighted sum
            portfolio_return = weight_spy * cum_return["SPY"] + weight_tlt * cum_return["TLT"]
            portfolio_std = weight_spy * std_dev["SPY"] + weight_tlt * std_dev["TLT"]

            # Modified Sharpe calculation
            sharpe = portfolio_return / (portfolio_std ** self.p.volatility_factor)

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_allocation = weight_spy

        return best_allocation

    def assign_equal_weight(self, today_date):
        """
        Assigns SPY and TLT weights based on the highest modified Sharpe ratio.
        """
        etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)
        lookback_data = etf_df.get(self.p.assets)

        best_spy_weight = self.modified_sharpe_ratio(lookback_data)
        weights = {"SPY": best_spy_weight, "TLT": 1.0 - best_spy_weight}

        return weights
