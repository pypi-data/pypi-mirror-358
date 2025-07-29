from types import SimpleNamespace
from backtrader_contrib.framework.lucid.data.data_adjuster import DataBundle


class LucidTAA:
    """
    Handles retrieval and transformation of historical market data.

    - Uses `DataBundle` to adjust price windows.
    - Ensures that all required market data is available for allocation computations.
    """

    def __init__(self, datas, csv_path, lookback_window=None):
        """
        Args:
            datas: List of Backtrader data feeds.
            csv_path: Path to CSV directory for `DataBundle`.
            lookback_window (int, optional): Number of historical days to consider.
        """
        if lookback_window is None:
            raise ValueError("Missing lookback window for DataBundle")

        self.lookback_window = lookback_window
        self.symbols = [data._name for data in datas]  # Extracts asset symbols from Backtrader feeds

        if csv_path is None:
            return

        self.adj_window = DataBundle(assets_list=self.symbols, csv_path=csv_path)
        self.adj_window.set_sliding_window(lookback=self.lookback_window)


class LucidAllocatorBase:
    """
    Base class for allocation strategies. Handles parameter management and interface for strategy design

    - Provides a structure for managing strategy parameters (`self.p`), using SimpleNamespace,
        making self.p clean and easy to use.
    - Handles data access through `LucidTAA`.
    - Defines required methods (`set_lookback_window`, `assign_equal_weight`) that must be implemented in subclasses.

    This is not a Backtrader `Strategy`, but an independent allocator to be used inside a strategy.
    """
    params = (
        ('nb_asset_in_portfolio', 0),
    )

    def __init__(self, **kwargs):
        """
        Initializes the allocation strategy with default parameters.

        Args:
            kwargs: Allows overriding default parameters.
        """
        params_dict = dict(self.params)

        # ✅ `self.p` holds strategy parameters, accessible like `self.p.nb_asset_in_portfolio`
        self.p = SimpleNamespace(**{key: kwargs.get(key, value) for key, value in params_dict.items()})

        self.lucid_taa = None  # Placeholder for data processing engine

    def set_lucid_taa(self, datas, csv_path, lookback_window):
        """
        Initializes `LucidTAA`, which handles data retrieval and processing.

        Args:
            datas (list): List of Backtrader data feeds.
            csv_path (str): Path to historical data in CSV format.
            lookback_window (int): Number of past periods to consider.
        """
        self.lucid_taa = LucidTAA(datas, csv_path, lookback_window)

    def set_lookback_window(self):
        """
        Defines the historical window size needed for calculations.

        Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement 'set_lookback_window()'")

    def assign_equal_weight(self, df):
        """
        Allocates weights to assets.

        Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement 'assign_equal_weight()'")
