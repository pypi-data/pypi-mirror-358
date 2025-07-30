from binance.client import Client
import pandas as pd
import os
from datetime import date

import warnings
warnings.filterwarnings("ignore")

class BN:
    def __init__(self) -> None:
        self.home = "%s" % (os.getenv('HOME'))
        self.csvDir = "%s/project/data/bn" % (self.home)
        self.market = "bn"
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(api_key, api_secret)
        self.start_date = '2017-01-01'
        today = date.today()
        self.end_date = today.strftime("%Y-%m-%d")
        self.interval = Client.KLINE_INTERVAL_1DAY
        # self.interval = Client.KLINE_INTERVAL_4HOUR


    def getK(self, _code):
        klines = self.client.get_historical_klines(_code, Client.KLINE_INTERVAL_1DAY, self.start_date, self.end_date)
        df = pd.DataFrame(klines, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        hist = df.drop(['timestamp', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore', 'index'], axis=1, errors="ignore")
        # print(hist.head())
        #hist = hist.reset_index() # already reset
        hist['Date'] = hist['Date'].dt.date
        hist = hist.set_index('Date')
        hist = hist.dropna()

        if len(hist) <= 10:
            return hist

        csvPath = "%s/%s.csv" % (self.csvDir, _code)
        print("--------", _code, csvPath)
        hist.to_csv(csvPath)
        return hist

    def getKFromList(self):
        # Define the file path
        list_path = "%s/project/data/list/bn.txt" % (self.home)

        try:
            with open(list_path, 'r') as file:
                for line in file:
                    code = line.strip()
                    print(code)
                    data = self.getK(code)
        except FileNotFoundError:
            print(f"File '{list_path}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__=="__main__":
    os.environ['https_proxy'] = 'http://127.0.0.1:7890'
    os.environ['http_proxy'] = 'http://127.0.0.1:7890'
    os.environ['all_proxy'] = 'socks5://127.0.0.1:7890'

    bn = BN()

    data = bn.getK('BTCUSDT')
    print(data)