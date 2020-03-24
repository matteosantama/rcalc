from flask import Flask, request, jsonify, Response
from slack import WebClient
import json
import os
import sys
import argparse



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
            exc.argument = self._get_action_from_name(exc.argument_name)
            raise exc
        super(ArgumentParser, self).error(message)



@app.route('/slack/calculate', methods=['POST'])
def receive_request():
    parser = argparse.ArgumentParser(description='Short-term lending calculator', prog='rcalc')

    parser.add_argument('rate', choices=['zq', 'sr1'], help='Specify whether to use zq or sr1')

    try:
        args = parser.parse_args(request.form['text'].split(' '))
    except argparse.ArgumentError as err:
        print(err)
        print('here')
        return 'errored'


    print(request.form)

    return 'no errors??'


# start the Flask server
if __name__ == "__main__":
    app.run()