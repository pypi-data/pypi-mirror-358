from backtrader_contrib.framework.lucid.utils.allocator_base import LucidAllocatorBase
import math
import pandas as pd


class DAAModel(LucidAllocatorBase):
    """
    https://indexswingtrader.blogspot.com/2018/12/exploring-smart-leverage-daa-on-steroids.html
    https://finimize.com/content/tactical-asset-allocation-part-one-sidestep-crashes-defensive-strategy

    for DAA we distinguish three universes: Risky (denoted eg. R12 when there are N=NR=12 risky assets),
    Protective (eg. P2, with NP=2 canary assets), and Cash (eg. C3 for NC=3 cash/bonds assets).

    there are two free parameters ie. the (risky) top T and the breadth parameter B (which determines the
    cash fraction, given the canary breadth).

    The cash fraction CF equals CF= b/B (max 100%), where b is related to the canary breadth: b is the number of
    bad canary assets (bad: with non-positive 13612W momentum). So with eg. B=2, we have CF=0, 50%, 100% for
    b=0,1,2+, respectively.

    The selection of the top T risky and the single cash/bond asset (if CF>0) are also based on fast (13612W) momentum.

    We will use Easy Trading (ET, see Keller 2017), so when eg. CF=50% and B=2, we only select the top T/2 risky
    assets, so eg. Top 3 when T=6.

    DAA-G12 we will use the same G12 and C3 risky and cash universe, together with the canary universe VWO/BND and
    breadth parameter B=2. The optimization of K25/IS results into best T=6 for DAA-G12, given P2=VWO/BND and
    B=2, see Fig. 8 DAA (2018) https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3212862

    """
    params = LucidAllocatorBase.params + (
        ('lookback_window', 252),  # 12m
        ('assets', ["SPY", "QQQ", "IWM", "VGK", "EWJ", "VWO", "GSG", "GLD", "VNQ", "HYG", "TLT", "LQD"]),
        ('offensive_trade', False),
        ('cash_proxy', ["SHY", "IEF", "LQD"]),  # US T-Bills as cash proxy
        ('canary', ["VWO", "BND"]),  # Canary asset
        ('breadth_parameter', 2),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Signals: SPY,QQQ,IWM,VGK,EWJ,VWO,GSG,GLD,VNQ,HYG, LQD,TLT + SHY,IEF
        # Trades: SSO,QLD,UWM,VGK,EWJ,VWO,GSG,GLD,URE,HYG,LQD,UBT + SHY,UST
        self.offensive_symbols = {
            'SPY': "SSO",
            'IWM': "UWM",
            'QQQ': "QLD",
            'VNQ': 'URE',
            'TLT': 'UBT',
            'IEF': 'UST',
        }

    def set_lookback_window(self):
        """ Ensure we have enough historical data for 1, 3, 6, and 12-month returns """
        return self.p.lookback_window

    def calculate_momentum(self, df, months):
        """
        Calculate momentum ensuring correct indexing when the first row is yesterday's price.
        """
        lookback_idx = months * 21  # Adjusted index since the first row is yesterday
        return (df.iloc[-1] / df.iloc[-lookback_idx]) - 1  # Compare yesterday's price to past price

    def switch_to_offensive(self, weights):
        """
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
        return {self.offensive_symbols.get(symbol, symbol): weight for symbol, weight in weights.items()}

    def assign_equal_weight(self, today_date):

        etf_df = self.lucid_taa.adj_window.get_adjusted_window(today_date=today_date)

        # Compute 13612W momentum for each asset
        mom1 = self.calculate_momentum(etf_df, months=1)
        mom3 = self.calculate_momentum(etf_df, months=3)
        mom6 = self.calculate_momentum(etf_df, months=6)
        mom12 = self.calculate_momentum(etf_df, months=12)

        # 13612W = ( 12 * r1 + 4 * r3 + 2 * r6 + 1 * r12 ) / 4
        # assets are tested on absolute momentum, but now using the responsive 13612W filter, resulting in a number of
        # assets with positive and non-positive momentum respectively (the so-called “bad” and “good” assets).
        fast_mom = (12 * mom1 + 4 * mom3 + 2 * mom6 + mom12) / 4

        # Get canary momentum
        canary_mom = fast_mom.loc[self.p.canary]
        b = (canary_mom < 0).sum()

        # Pick the best asset in the “risk-off” universe as safety asset for “cash”
        top_risk_off = fast_mom.loc[self.p.cash_proxy].nlargest(1).index[0]

        # Compute the number of assets with non-positive momentum in the “risk-on” universe (b)
        #  absolute momentum is applied for establishing a universe’s breadth momentum. Next, our new breadth
        #  protection threshold B is defined as the minimum number of “bad” assets (b) for which the strategy is 100%
        #  invested in a “risk-off” asset (“cash”). For an N-sized “risk-on” universe, a portfolio’s cash fraction (CF)
        #  is determined by the ratio b/B. In formula:
        # CF=b/B with 0<=CF<=1 limits, where b=0,1,..,N and B<=N.
        CF = min(1, b / self.p.breadth_parameter)

        # 1. When both canary assets VWO and BND register negative 13612W momentum, invest 100% in the single best
        # bond of the cash universe;
        # 2. When only one of the canary assets VWO or BND registers negative momentum, allocate 50% in the top half of
        # the best risky assets, while applying equal weights, and invest the remaining 50% in the best bond of the
        # cash universe;
        # 3. When none of canary assets VWO and BND register negative momentum, indicating the risk of a crash is deemed
        # low, invest 100% in the full top risky assets, again applying equal weights.

        # Select risk-on assets
        num_risk_assets = self.p.nb_asset_in_portfolio if CF == 0 else self.p.nb_asset_in_portfolio // 2
        top_risk_on = fast_mom.loc[self.p.assets].nlargest(num_risk_assets).index.tolist()

        # Replace any negative momentum risk-on assets with top risk-off asset
        #top_risk_on = [asset if fast_mom[asset] >= 0 else top_risk_off for asset in top_risk_on]
        # Remove duplicates while maintaining order
        #top_risk_on = list(dict.fromkeys(top_risk_on))

        # Assign weights
        weights = {top_risk_off: CF}

        if top_risk_on:
            eq_weight = (1 - CF) / len(top_risk_on)
            weights.update({asset: eq_weight for asset in top_risk_on})

        if self.p.offensive_trade:
            weights = self.switch_to_offensive(weights)


        return weights
