import os
import akshare as ak
import warnings
warnings.filterwarnings("ignore")

class AKER:
    def __init__(self, _market='cn') -> None:
        self.market = _market

        self.home = "%s" % (os.getenv('HOME'))
        self.csvDir = f'{self.home}/project/data/{self.market}'

    def getK(self, _code):
        try:
            adjust = 'qfq'
            if self.market == 'hk':
                hist = ak.stock_hk_daily(symbol=_code, adjust=adjust)
            else:
                hist = ak.stock_zh_a_hist(symbol=_code, period="daily", adjust=adjust)
        except Exception as e:
            print(f'failed: {e}')
            return None

        #print(hist.head())
        if len(hist) <= 10:
            return hist

        if self.market == 'hk':
            hist.columns = ["Date", "Open", "High",  "Low", "Close", "Volume"]
            hist['Code'] = _code
            #hist['Date'] = hist['Date'].dt.date
        else:
            hist = hist.drop('振幅', axis=1, errors="ignore")
            hist = hist.drop('涨跌额', axis=1, errors="ignore")
            hist.columns = ["Date", "Code", "Open", "Close",  "High", "Low", "Volume", "Amount", "Incr", "TurnOver"]
        hist = hist.reset_index()
        hist = hist.set_index('Date')
        hist = hist.dropna()
        csvPath = "%s/%s.csv" % (self.csvDir, _code)
        #print("--------", _code, csvPath)
        hist.to_csv(csvPath)
        return hist

    def getListPath(self):
        # Define the file path
        list_path = "%s/project/data/list/cn.txt" % (self.home)
        if self.market == 'hk':
            list_path = "%s/project/data/list/hk.txt" % (self.home)
        return list_path

    def getKFromList(self):
        # Define the file path
        list_path = "%s/project/data/list/cn.txt" % (self.home)
        if self.market == 'hk':
            list_path = "%s/project/data/list/hk.txt" % (self.home)

        try:
            with open(list_path, 'r') as file:
                for line in file:
                    code = line.strip()
                    print(code)
                    _ = self.getK(code)
        except FileNotFoundError:
            print(f"File '{list_path}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__=="__main__":
    # h = AKER('hk')
    # data = h.getK('00700')
    # print(data)

    # a = AKER()
    # data = a.getK('601088')
    # print(data)


    # prototype
    # code = '601088'
    # adjust = 'qfq'
    # hist = ak.stock_zh_a_hist(symbol=code, period="daily", adjust=adjust)
    # print(hist)

    code = '600519'
    code = '601088'
    hist = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
    print(hist.head())
    print(hist.tail())