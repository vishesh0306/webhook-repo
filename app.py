from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb+srv://dudejavishesh363:VE0GLXqnxpPIRimY@cluster0.ttgwu.mongodb.net/?retryWrites=true&w=majority&appName=cluster0')
db = client.githubEvents
events_collection = db.events

# Check MongoDB connection
print(client.list_database_names())

@app.route('/webhook', methods=['POST'])
def github_webhook():
    data = request.json

    # Log the received JSON body for debugging
    print("Received JSON:", data)

    # Default timestamp
    timestamp = datetime.now()

    # Handle push events (since there's no action field)
    if 'ref' in data and 'commits' in data:
        ref = data.get('ref')
        commits = data.get('commits', [])
        pusher = data.get('pusher', {})
        repository = data.get('repository', {})
        branch = ref.split('/')[-1] if ref else 'unknown'

        # Log commit details
        event_data = {
            'actionType': 'PUSH',
            'pusher': pusher.get('name', 'unknown'),
            'repository': repository.get('full_name', 'unknown'),
            'branch': branch,
            'timestamp': timestamp,
            'commit_count': len(commits),
            'commits': []
        }

        # Process each commit
        for commit in commits:
            commit_info = {
                'id': commit.get('id'),
                'message': commit.get('message'),
                'url': commit.get('url'),
                'author': commit.get('author', {}).get('name', 'unknown'),
                'committer': commit.get('committer', {}).get('name', 'unknown')
            }
            event_data['commits'].append(commit_info)

        # Insert the event data into MongoDB
        events_collection.insert_one(event_data)
        return jsonify({'message': 'Push event saved', 'event': event_data}), 201
    else:
        # If the event is unsupported, return an error
        return jsonify({'message': 'Unsupported event or no action field'}), 400

# Serve the HTML UI
@app.route('/')
def index():
    return render_template('index.html')

# Fetch the latest events for UI (last 10 events)
@app.route('/events', methods=['GET'])
def get_events():
    events = list(events_collection.find().sort('timestamp', -1).limit(10))
    for event in events:
        event['_id'] = str(event['_id'])  # Convert ObjectId to string for JSON serialization
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
