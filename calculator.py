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
        self.df = None  # will get populated by self.query_data()


    def query_data(self):
        yesterday = dt.datetime.today() - dt.timedelta(days=1)
        week_into_prev_month = yesterday.replace(day=1) - dt.timedelta(days=7)
        datefmt = '%m%d%Y'

        # format endpoint given contract type and dates to query
        endpoint = Calculator.ENDPOINTS[self.contract].format(
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
        df = pd.DataFrame.from_dict(data, orient='index', columns=[self.contract])
        df.index = pd.DatetimeIndex(df.index).normalize()
        df = df.reindex(pd.date_range(
            start=yesterday.replace(day=1), 
            end=yesterday, 
            freq='D'), method='bfill')
        # get rid of time information and rename index as 'date'
        df.index = df.index.normalize().rename('date')

        # compute rolling mean and implied futures price
        df['rolling_mean'] = df[self.contract].expanding().mean()
        df['fut_price'] = 100 - df['rolling_mean']

        # store dataframe as property for later access
        self.df = df


    def compute_futures_price(self) -> str:
        price = 100 - self.df[self.contract].mean()
        base = 0.0025
        return f'{base * round(price / base):.4f}'


if __name__ == "__main__":
    calc = Calculator('zq')
    calc.query_data()
    print(calc.df)