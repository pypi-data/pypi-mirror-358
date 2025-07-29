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

import numpy as np
import pandas as pd
import cvxpy as cv

from pypfopt import expected_returns
from pypfopt import risk_models
from pypfopt.efficient_frontier import EfficientFrontier


class PortfolioOptimization(object):

    def __init__(self, today_date, risk_free_rate=0,
                 momentum_lookback=180, volatility_window=20, set_nlargest=5,
                 use_corr=False, df_mom_vol=None):

        # and chooses the top five ETFs
        window_returns = np.log(df_mom_vol.iloc[-1]) - np.log(df_mom_vol.iloc[0])
        nlargest = list(window_returns.nlargest(set_nlargest).index)

        '''
        # using the slope to get the momentum
        wret = {}
        for _el in df_mom_vol:
            returns = np.log(df_mom_vol[_el])
            x = np.arange(len(returns))
            slope, _, rvalue, _, _ = linregress(x, returns)
            wret[_el] = slope

        nlargest = list(pd.Series(wret).nlargest(set_nlargest).index)
        '''

        # applies a percentage allocation to the chosen ETFs which minimizes the variance of the overall portfolio
        # based on the last 20 trading days.
        # -> stock_price used for minimizing volatility on the last 20 trading days.
        portfolio_price = df_mom_vol[-volatility_window:][nlargest]

        self.stock_price = portfolio_price
        self.nlargest = nlargest
        self.use_corr = use_corr
        self.daily_return = self.stock_price.pct_change().dropna()
        self.risk_free_rate = risk_free_rate
        # self.n = len(self.stock_price) # numbers of risk assets in portfolio
        # use .corr() rather than .cov() to optimize portfolio
        self.use_corr = use_corr

        self.min_weight = 0
        self.max_weight = 1
        self.aaa_weights = None
        return

    def set_weight_constraints(self, min_w=0.0, max_w=1.0):
        self.min_weight = min_w
        self.max_weight = max_w

    def minvar_weights(self, cvxpy=False, pypfopt=False):
        if cvxpy:
            return self.cvxpy_minvar()
        elif pypfopt:
            return self.pypfopt_minvar()

    def cvxpy_minvar(self):

        self.mu = np.matrix(self.daily_return.mean(axis=0).values)

        # Covariance or Correlation matrix
        if self.use_corr:
            self.sigma = self.daily_return.corr().values
        else:
            self.sigma = self.daily_return.cov().values
            # self.sigma = self.daily_return.apply(lambda x: np.log(1+x)).cov().values

        w = cv.Variable((self.mu.shape[1], 1))
        """
        MV model Variables
        """
        risk = cv.quad_form(w, self.sigma)

        constraints = [cv.sum(w) == 1]
        constraints.append(w >= self.min_weight)
        constraints.append(w <= self.max_weight)

        prob = cv.Problem(cv.Minimize(risk), constraints)
        prob.solve()

        weights = np.matrix(w.value).T
        weights = weights / np.sum(weights)
        weights = np.squeeze(np.array(weights))

        # TEST
        returns = self.daily_return
        num_assets = len(self.nlargest)

        # Covariance or Correlation matrix
        if self.use_corr:
            matrix = returns.corr()
            # matrix = returns.apply(lambda x: np.log(1+x)).corr()
        else:
            matrix = returns.cov()
            # matrix = returns.apply(lambda x: np.log(1+x)).cov()

        # Variables and constraints
        weights = cv.Variable(num_assets)
        risk = cv.quad_form(weights, matrix)
        constraints = [weights >= self.min_weight, weights <= self.max_weight, cv.sum(weights) == 1]

        # Objective function (minimize portfolio variance)
        obj = cv.Minimize(risk)

        # Create and solve the problem
        problem = cv.Problem(obj, constraints)
        problem.solve()

        # Get allocation weights
        weights_df = pd.DataFrame(list(weights.value), index=list(self.nlargest), columns=["Mean_Variance"])
        self.aaa_weights = weights_df
        return weights_df

    def pypfopt_minvar(self):
        # Annualized Returns calculation
        returns = expected_returns.mean_historical_return(self.stock_price)
        mu = expected_returns.capm_return(self.stock_price)

        # Covariance or Correlation matrix
        sigma = risk_models.sample_cov(self.stock_price, frequency=252)
        sigma = risk_models.CovarianceShrinkage(self.stock_price).ledoit_wolf(shrinkage_target='single_factor')
        # sigma = risk_models.CovarianceShrinkage(self.stock_price).oracle_approximating()

        if self.use_corr:
            sigma = risk_models.cov_to_corr(sigma)

        # ef = EfficientFrontier(returns, variance , weight_bounds=(0, 1))
        # ef.max_quadratic_utility(1)
        ef = EfficientFrontier(mu, sigma, weight_bounds=(self.min_weight, self.max_weight))  # setup
        # ef.add_objective(objective_functions.L2_reg)  # add a secondary objective

        # ef.max_quadratic_utility()
        ef.min_volatility()

        # Getting the optimal weights from the optimization
        weights = ef.clean_weights()
        # Add weights to the weighs dataframe
        weights_df = pd.DataFrame(list(weights.values()), index=list(weights.keys()), columns=["Mean_Variance"])
        self.aaa_weights = weights_df
        return weights_df


if __name__ == "__main__":
    import pathlib
    from backtrader_contrib.framework.lucid.data.data_adjuster import DataBundle

    momentum_lookback = 180
    volatility_lookback = 20
    today_date = pd.Timestamp('2023-09-21')

    # revisited symbols: 2015
    # The 9 asset classes are as follows: U.S. Large Cap Equity, U.S. Small Cap Equity, NASDAQ 100 Equity,
    # U.S. Real Estate, U.S. Long Term Treasury Bonds, Emerging Markets Equity, International Developed Markets Equity, Gold, and Commodities.
    symbols = ['SPY', 'IWM', 'QQQ', 'IYR', 'TLT', 'EEM', 'EFA', 'GLD', 'DBC']
    # original: 2012
    # symbols = ['SPY', 'IWM', 'EWJ', 'IYR', 'RWX', 'TLT', 'IEF', 'EEM', 'EFA', 'GLD', 'DBC']

    csv_path = pathlib.Path(__file__).parent.parent.parent.parent.parent.parent.joinpath('data/as_traded')

    adj_window = DataBundle(assets_list=symbols, csv_path=csv_path)
    adj_window.set_sliding_window(lookback=max(momentum_lookback, volatility_lookback))
    etf_df = adj_window.get_adjusted_window(today_date=today_date.date())

    #adj_window.sliding_start_date = '2023-02-14'
    #adj_window.sliding_end_date = '2023-09-21'
    #etf_df = adj_window.get_adjusted_window(manual_window=True)

    adaptive_portf = PortfolioOptimization(today_date=adj_window.sliding_start_date, use_corr=False,
                                           momentum_lookback=momentum_lookback,
                                           set_nlargest=5,
                                           volatility_window=volatility_lookback, df_mom_vol=etf_df)
    adaptive_portf.set_weight_constraints(min_w=0.05, max_w=0.7)
    updated_allocation = adaptive_portf.minvar_weights(cvxpy=False, pypfopt=True)

    print(f"DataBundle adaptive portfolio weights: {adaptive_portf.aaa_weights}")

