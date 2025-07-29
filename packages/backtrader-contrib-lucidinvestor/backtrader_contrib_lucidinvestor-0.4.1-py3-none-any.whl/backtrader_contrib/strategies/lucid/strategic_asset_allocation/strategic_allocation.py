from backtrader_contrib.framework.lucid.utils.allocator_base import LucidAllocatorBase


class StrategicAllocation(LucidAllocatorBase):
    """
    Implements a **fixed-weight** strategic asset allocation model.
    Keeps allocation logic separate from Backtrader execution logic.

    - Inherits from `LucidAllocatorBase`, meaning it follows the standard allocator structure.
    - Uses predefined **static weights** for each asset.
    - Works within a Backtrader strategy but is **not a Backtrader `Strategy` itself**.
    """
    params = LucidAllocatorBase.params + (
        ('fixed_weights', {"AssetSymbol": 0}),  # Default: Empty weight dictionary
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fixed_weights = self.p.fixed_weights  # Access fixed weights from `params`

    def set_lookback_window(self, df=None):
        """
        Not required for fixed target allocation (returns a placeholder value).
        """
        return 1  # Lookback window is irrelevant for fixed allocation

    def assign_equal_weight(self, today_date):
        """
        Returns the predefined fixed weight allocation.
        """
        #etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)
        allocation = { asset.symbol: asset.allocation for asset in self.fixed_weights.assets.values() }

        return allocation
