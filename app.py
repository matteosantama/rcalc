from flask import Flask, request
from slack import WebClient
import os
import argparse
import datetime as dt
from calculator import Calculator
from pprint import pformat


# configure slack client by loading token from environment
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
slack_client = WebClient(token=SLACK_BOT_TOKEN)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)


class ArgumentParser(argparse.ArgumentParser):
    """
    Custom implementation of argparse module that supports raising exceptions
    on errors instead of just printing and exiting
    """
    
    def error(self, message):
        raise argparse.ArgumentError(None, message)


@app.route('/slack/calculate', methods=['POST'])
def receive_request():
    
    parser = ArgumentParser(
        description=("Short-term lending rate calculator. ") + 
        ("Note that settlments are precise to 3 decimal places, but front month ") +
        ("futures are quoted to 4 decimal places. Hence, the offical vs. exact settlement values"), 
        prog='rcalc', add_help=False
    )
    group = parser.add_mutually_exclusive_group()
    
    parser.add_argument('symbol', 
        choices=['zq', 'sr1'], help='Specify whether to use zq or sr1'
    )
    group.add_argument('-h', '--help', 
        action='store_true', dest='help'
    )
    group.add_argument('-v', '--verbose', 
        action='store_true', dest='verbose', help='Use this flag to print rate dataframe'
    )
    group.add_argument('-r', '--rate', 
        type=float, dest='rate', help='Assign a rate to the remaining days'
        )
    group.add_argument('-s', '--settle', 
        type=float, dest='settle', 
        help='Determine the average rate we must see to achieve the target settle ex). 99.8725'
    )
    
    # try to parse args, return failure string if unable to
    try:
        args = parser.parse_args(request.form['text'].split(' '))
    except argparse.ArgumentError as err:
        return err.message

    # return help string if flag is present
    if args.help:
        return parser.format_help()
    
    calculator = Calculator(args.symbol)

    if args.verbose:
        return '.' + calculator.df.to_string(justify='right')
    
    response = dict()
    response['official_settle'] = calculator.compute_futures_price()
    response['exact_settle'] = calculator.compute_futures_price(official=False)

    if args.rate:
        response['submitted rate'] = args.rate
        response['price with rate'] = calculator.find_price_with_rate(args.rate)
    if args.settle:
        response['submitted price'] = args.settle
        response['rate needed'] = calculator.find_rate_with_price(args.settle)

    # Heroku is configured to America/New York tz
    if dt.datetime.now().time() < dt.time(hour=9):
        response['WARNING'] = 'Upcoming data release at 8am Central'

    return pformat(response)


# start the Flask server
if __name__ == "__main__":
    app.run()