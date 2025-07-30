import os
import yfinance as yf

import warnings
warnings.filterwarnings("ignore")

class Yahooer:
    def __init__(self) -> None:
        self.market = "us"

        self.home = "%s" % (os.getenv('HOME'))

        self.cacheDir = "%s/%s" % (self.home, ".cache/yf")
        yf.set_tz_cache_location(self.cacheDir)

        self.csvDir = "%s/project/data/yf" % (self.home)

    def getK(self, _code):
        msft = yf.Ticker(_code)
        hist = msft.history(period="max")
        if len(hist) <= 10:
            return hist
        #print(hist.head())
        hist = hist.drop('Dividends', axis=1, errors="ignore")
        hist = hist.drop('Stock Splits', axis=1, errors="ignore")
        hist = hist.drop('Capital Gains', axis=1, errors="ignore")
        hist = hist.reset_index()
        hist['Date'] = hist['Date'].dt.date
        hist = hist.set_index('Date')
        hist = hist.dropna()
        csvPath = "%s/%s.csv" % (self.csvDir, _code)
        #print("--------", _code, csvPath)
        hist.to_csv(csvPath)
        return hist

    def getListPath(self):
        list_path = "%s/project/data/list/us.txt" % (self.home)
        return list_path

    def getKFromList(self):
        # Define the file path
        list_path = "%s/project/data/list/us.txt" % (self.home)

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
    y = Yahooer()
    y.getK('IONQ')
    # ya.getKFromList()
