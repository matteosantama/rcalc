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
    on errors instead of just silently exiting
    """

    def error(self, message):
        exc = sys.exc_info()[1]
        if exc:
            exc.user_message = message
            raise exc
        super(ArgumentParser, self).error(message)



@app.route('/slack/calculate', methods=['POST'])
def receive_request():
    parser = ArgumentParser(description='Short-term lending calculator', prog='rcalc')

    parser.add_argument('rate', choices=['zq', 'sr1'], help='Specify whether to use zq or sr1')

    # try to parse args, return failure string if unable to
    try:
        args = parser.parse_args(request.form['text'].split(' '))
    except argparse.ArgumentError as err:
        return err.user_message

    calculator = Calculator(args.rate)

    return calculator.endpoint



# start the Flask server
if __name__ == "__main__":
    app.run()