from flask import Flask, request
from slack import WebClient
import json
import os
import sys
import argparse
from calculator import Calculator


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
    parser = ArgumentParser(description='Short-term lending rate calculator', prog='rcalc', add_help=False)
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
    group.add_argument('-t', '--target', 
        type=float, dest='target', help='Determine the average rate we must see to achieve the target price'
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
    calculator.query_data()

    if args.verbose:
        return '.' + calculator.df.to_string()

    response = dict()
    response['futures price'] = calculator.compute_futures_price()
    return response


# start the Flask server
if __name__ == "__main__":
    app.run()