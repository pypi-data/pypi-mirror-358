#!/usr/bin/env python
# -*- encoding: utf8 -*-

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

from jing.data_center import DataCenter
from jing.reference import Reference
from jing.rule_set import RuleSet

from jing.rule import RuleSimple
from jing.rule import RulePriceBreakout

pd.set_option('display.max_columns', None)

class X:
    def __init__(self, _market="cn", _date="", _code="") -> None:
        self.market = _market
        self.date = _date
        self.data_center = DataCenter()
        self.rule_map = {}
        self.result = []

        if len(_code) > 0:
            self.listing = pd.DataFrame({'code':[_code]})
        else:
            self.listing = self.data_center.list(market=_market)

    def get_list(self):
        return self.listing

    def get_result(self):
        return self.result

    def add_rule(self, _rule_class):
        #print(f'_rule_class.__name__: {_rule_class.__name__}')
        self.rule_map[_rule_class.__name__] = _rule_class

    def run(self, _lookBack=0):
        for i, row in self.listing.iterrows():
            code = row['code']
            print(f"--{code}")
            self.run_one_stock(code, _lookBack)

    def run_one_stock(self, _code, _lookBack=0):
        self.one = self.data_center.one(_code, self.date)
        if len(self.one) < 400:
            print(f"{_code} -- bye")
            return

        self.ref = Reference(self.one)

        rs = RuleSet(_code, self.ref)
        for rule_name, rule_class in self.rule_map.items():
            rs.add_rule(rule_class)
            #print(f"rule[{rule_name}]")
        rs.run()
        results = rs.get_result()
        if len(results) > 0:
            self.result.append(results)

if __name__=="__main__":
    # x = X("us", "2023-10-30")

    # ma50 - ma200
    # x = X("us", "2023-10-30", "NFLX")
    # x = X("us", "2023-11-01", "AMD")
    # x.run()

    # breakout +
    # x = X("us", "2024-01-19", "SMCI") # breakout

    # x = X("us", "2023-05-24", "ANF", "volumeBreakout")
    # x = X("us", "2024-01-19", "SMCI", "volumeBreakout")
    # x.run()
    #x = X("us", "2024-02-16")

    #x = X("us", "2024-05-25")
    #x.run(5)

    # x = X("us", "2024-09-27", "IONQ")
    # x.add_rule(RuleSimple)
    # x.run()

    # x = X("us", "2024-09-27")
    # x.add_rule(RuleSimple)
    # x.run()

    x = X("us", "2024-01-19", "SMCI")
    x.add_rule(RulePriceBreakout)
    x.add_rule(RuleSimple)
    x.run()
    print(x.result)

