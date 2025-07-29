from backtrader_contrib.framework.lucid.utils.allocator_base import LucidAllocatorBase
from adaptive_allocation_methods import PortfolioOptimization


class AdaptiveAllocation(LucidAllocatorBase):
    """
    integrates well with Backtrader’s optimization engine.
    """
    params = LucidAllocatorBase.params + (
        ('momentum_window', 180),
        ('volatility_window', 20),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_lookback_window(self):
        """
        Defines the lookback window based on the longest period used in TRank computation.
        """
        return max(self.p.momentum_window, self.p.volatility_window)

    def assign_equal_weight(self, today_date):
        """
        Selects top ETFs based on TRank and assigns equal weights.

        Args:
            df (pd.DataFrame): DataFrame containing asset prices.

        Returns:
            dict: Dictionary with selected ETFs and their equal weights.
        """
        etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)

        adaptive_portf = PortfolioOptimization(today_date=today_date, use_corr=False,
                                               momentum_lookback=self.p.momentum_window,
                                               set_nlargest=self.p.nb_asset_in_portfolio,
                                               volatility_window=self.p.volatility_window,
                                               df_mom_vol=etf_df)
        adaptive_portf.set_weight_constraints(min_w=0.05, max_w=0.7)
        updated_allocation = adaptive_portf.minvar_weights(cvxpy=True, pypfopt=False)

        return updated_allocation['Mean_Variance']
