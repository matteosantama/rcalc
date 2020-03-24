import pandas as pd
import datetime as dt


class Calculator:
    """
    This class handles all the data computations. It requests the data, parses the XML,
    and then does the calculations to compute the monthly average
    """

    ENDPOINTS = {
        'sr1': """https://websvcgatewayx2.frbny.org/mktrates_external_httponly\
        /services/v1_0/mktRates/xml/retrieve?typ=RATE&f={}&t={}""",
        'zq': """https://websvcgatewayx2.frbny.org/autorates_fedfunds_external\
        /services/v1_0/fedfunds/xml/retrieve?typ=RATE&f={}&t={}"""
    }

    def __init__(self, contract):
        today = dt.datetime.today()
        first_of_the_month = today.replace(day=1)
        datefmt = '%m%d%Y'

        self.endpoint = Calculator.ENDPOINTS[contract].format(
            first_of_the_month.strftime(datefmt),
            today.strftime(datefmt)
        )