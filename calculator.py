import pandas as pd
import datetime as dt
import requests
from xml.etree import ElementTree


class Calculator:
    """
    This class handles all the data computations. It requests the data, parses the XML,
    and then does the calculations to compute the monthly average
    """

    ENDPOINTS = {
        'sr1': 'https://websvcgatewayx2.frbny.org/mktrates_external_httponly/services/v1_0/mktRates/xml/retrieve?typ=RATE&f={}&t={}',
        'zq': 'https://websvcgatewayx2.frbny.org/autorates_fedfunds_external/services/v1_0/fedfunds/xml/retrieve?typ=RATE&f={}&t={}'
    }


    def __init__(self, contract):
        self.contract = contract
        self.df = Calculator.construct_df(contract)


    @staticmethod
    def construct_df(contract):
        yesterday = dt.datetime.today() - dt.timedelta(days=1)
        week_into_prev_month = yesterday.replace(day=1) - dt.timedelta(days=7)
        datefmt = '%m%d%Y'

        # format endpoint given contract type and dates to query
        endpoint = Calculator.ENDPOINTS[contract].format(
            week_into_prev_month.strftime(datefmt),
            yesterday.strftime(datefmt)
        )
        response = requests.get(endpoint)

        # find and parse rate date from XML feed
        tree = ElementTree.fromstring(response.content)
        dataset = tree.find('{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message}DataSet')
        series = dataset.find("./Series[@FUNDRATE_OBS_POINT='50%']")
        data = dict()
        for obs in series.iter('Obs'):
            data[obs.attrib['TIME_PERIOD']] = float(obs.attrib['OBS_VALUE'])

        # construct df and fill missing days
        df = pd.DataFrame.from_dict(data, orient='index', columns=[contract])
        df.index = pd.DatetimeIndex(df.index).normalize() # normalize to midnight since timestamp isnt useful
        df = df.reindex(pd.date_range(
            start=yesterday.replace(day=1), 
            end=yesterday, 
            freq='D'), method='bfill')
        # get rid of time information and rename index as 'date'
        df.index = df.index.normalize().rename('date')

        # compute rolling mean and implied futures price
        df['rolling_mean'] = df[contract].expanding().mean()
        df['fut_price'] = 100 - df['rolling_mean']

        return df

    
    def find_price_with_rate(self, rate: float) -> str:
        """
        These methods return properly formatted strings
        """
        first = self.df.index.min()
        complete_idx = pd.date_range(start=first, periods=first.days_in_month, freq='D')
        df = self.df[self.contract].reindex(index=complete_idx, fill_value=rate)

        return Calculator._format_from_rate(df.mean())

    
    def find_rate_with_price(self, price: float) -> str:
        """
        These methods return properly formatted strings
        """
        dim = self.df.index.min().days_in_month
        days_left = dim - len(self.df.index)

        seen_sum = self.df[self.contract].sum()
        end_rate = 100 - price

        req_rate = ( (end_rate * dim) - seen_sum ) / days_left
        return f'{req_rate:.5f}'


    def compute_futures_price(self) -> str:
        return Calculator._format_from_rate(self.df[self.contract].mean())

    
    @staticmethod
    def _format_from_rate(avg_daily_rate) -> str:
        """
        round and format a futures price to 4 decimals
        """
        settlement = 100 - round(avg_daily_rate, 3)
        return f'{settlement:.4f}'


if __name__ == "__main__":
    calc = Calculator('zq')
    print(calc.df)
    print(calc.compute_futures_price())