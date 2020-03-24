from flask import Flask, request, jsonify, Response
from slack import WebClient
import json
import os


# configure slack client for handling requests
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
slack_client = WebClient(token=SLACK_BOT_TOKEN)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)


@app.route('/slack/calculate', methods=['POST'])
def calculate():
    print('here we are')

    print(request.form["payload"])
    
    # parse the request payload
    form_json = json.loads(request.form["payload"])

    print('here!')
    # return Response(json.dumps(form_json), mimetype='application/json')
    
    return jsonify(
        response_type='in_channel',
        text='<https://youtu.be/frszEJb0aOo|General Kenobi!>',
    )


# start the Flask server
if __name__ == "__main__":
    app.run()