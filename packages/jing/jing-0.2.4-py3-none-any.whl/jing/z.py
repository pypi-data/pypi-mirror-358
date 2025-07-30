#!/usr/bin/env python
# -*- encoding: utf8 -*-

from jing.yahooer import Yahooer
from jing.aker import AKER

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

pd.set_option('display.max_columns', None)

class Z:
    def __init__(self, _market="us") -> None:
        self.market = _market
        if self.market == 'us':
            self.inst = Yahooer()
        elif self.market == 'hk' or self.market == 'cn':
            self.inst = AKER(self.market)
        else:
            self.inst = Yahooer()

    def download(self, _code=""):
        self.code = _code
        if len(_code) > 0:
            self.inst.getK(self.code)
        else:
            self.inst.getKFromList()

if __name__=="__main__":
    # z = Z()
    # z.download("PLTR")
    z2 = Z(_market='cn')
    z2.download('600863')
