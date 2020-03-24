from flask import Flask, request, make_response, Response
# from slackclient import SlackClient
from slack import WebClient
import json


# configure slack client for handling requests
SLACK_BOT_TOKEN = 'todo'
slack_client = WebClient(SLACK_BOT_TOKEN)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)


@app.route('/slack/calculate', methods=['POST'])
def calculate():
    # parse the request payload
    form_json = json.loads(request.form["payload"])

    return Response(json.dumps(form_json), mimetype='application/json')


# start the Flask server
if __name__ == "__main__":
    app.run()