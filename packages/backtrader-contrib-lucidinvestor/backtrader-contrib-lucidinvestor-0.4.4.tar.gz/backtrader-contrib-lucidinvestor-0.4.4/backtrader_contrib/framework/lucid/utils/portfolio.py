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


# https://levelup.gitconnected.com/how-to-deserialize-json-to-custom-class-objects-in-python-d8b92949cd3b
import json
import ast


class Asset:
    def __init__(self, symbol, allocation, currency):
        self.symbol = symbol
        self.allocation = allocation
        self.currency = currency


class Portfolio:
    def __init__(self, assets=None, asset_as_dict=None, import_obj=None, **kwargs):

        if assets is not None:
            for el in assets:
                if not isinstance(assets[el], Asset):
                    exit("'assets' only takes a dictionary of Asset as input. Clean Exit().")

        self.assets = assets or dict()

        if asset_as_dict is not None:
            self.import_dict(asset_as_dict)

        self.allocation_by_currency = {'USD': 0.990}

        if import_obj is not None:
            self.fromobj(import_obj)

    def import_dict(self, assets):
        if not isinstance(assets, dict):
            exit("'import_dict' only takes a dictionary of {symbol-allocation-currency} as input. Clean Exit().")

        for el in assets:
            symbol = assets[el]['symbol']
            allocation = assets[el]['allocation']
            currency = assets[el]['currency']
            self.add_asset(Asset(
                symbol=symbol,
                allocation=allocation,
                currency=currency
            ))

    def add_asset(self, asset):
        self.assets[asset.symbol] = Asset(
            symbol=asset.symbol,
            allocation=asset.allocation,
            currency=asset.currency
        )

    def tojson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def fromobj(self, obj):
        if isinstance(obj, str):
            temp = ast.literal_eval(obj)
            self.assets = dict()
            self.import_dict(temp['assets'])

            self.allocation_by_currency = temp['allocation_by_currency']
        else:
            exit("'fromobj' only takes a str to 'ast.literal_eval of as input. Clean Exit().")

    def get_portfolio_allocation(self, currency):
        if currency in self.allocation_by_currency:
            return self.allocation_by_currency[currency]
        else:
            return None
