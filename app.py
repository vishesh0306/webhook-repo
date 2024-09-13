from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB (local or use MongoDB Atlas for cloud)
client = MongoClient('mongodb://localhost:27017/')
db = client.githubEvents
events_collection = db.events

@app.route('/webhook', methods=['POST'])
def github_webhook():
    data = request.json
    action = data.get('action')
    sender = data.get('sender', {})
    ref = data.get('ref')
    pull_request = data.get('pull_request')
    timestamp = datetime.utcnow()

    event_data = None

    # Handle Push Event
    if action == 'push':
        event_data = {
            'actionType': 'PUSH',
            'author': sender.get('login'),
            'toBranch': ref.split('/')[-1],
            'timestamp': timestamp
        }

    # Handle Pull Request Event
    elif action == 'pull_request':
        event_data = {
            'actionType': 'PULL_REQUEST',
            'author': sender.get('login'),
            'fromBranch': pull_request.get('head').get('ref'),
            'toBranch': pull_request.get('base').get('ref'),
            'timestamp': timestamp
        }

    # Save event to MongoDB
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
