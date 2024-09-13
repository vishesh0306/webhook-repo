from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb+srv://dudejavishesh363:VE0GLXqnxpPIRimY@cluster0.ttgwu.mongodb.net/?retryWrites=true&w=majority&appName=cluster0')
db = client.githubEvents
events_collection = db.events

@app.route('/webhook', methods=['POST'])
def github_webhook():
    data = request.json
    action = data.get('action')
    sender = data.get('sender', {})
    ref = data.get('ref')
    pull_request = data.get('pull_request')
    timestamp = datetime.now()

    event_data = None

    if action == 'push':
        event_data = {
            'actionType': 'PUSH',
            'author': sender.get('login'),
            'toBranch': ref.split('/')[-1],
            'timestamp': timestamp
        }
    elif action == 'pull_request':
        event_data = {
            'actionType': 'PULL_REQUEST',
            'author': sender.get('login'),
            'fromBranch': pull_request.get('head').get('ref'),
            'toBranch': pull_request.get('base').get('ref'),
            'timestamp': timestamp
        }
    elif action == 'merged':
        event_data = {
            'actionType': 'MERGE',
            'author': sender.get('login'),
            'fromBranch': pull_request.get('head').get('ref'),
            'toBranch': pull_request.get('base').get('ref'),
            'timestamp': timestamp
        }

    if event_data:
        events_collection.insert_one(event_data)
        return jsonify({'message': 'Event saved'}), 201
    else:
        return jsonify({'message': 'Unsupported event'}), 400

# Endpoint to serve events to the UI
@app.route('/events', methods=['GET'])
def get_events():
    events = list(events_collection.find().sort('timestamp', -1).limit(10))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
