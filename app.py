from flask import Flask, request, jsonify, render_template, abort
from pymongo import MongoClient
from datetime import datetime
import hmac
import hashlib

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb+srv://dudejavishesh363:VE0GLXqnxpPIRimY@cluster0.ttgwu.mongodb.net/?retryWrites=true&w=majority&appName=cluster0')
db = client.githubEvents
events_collection = db.events


#check

print(client.list_database_names())



# Webhook secret (replace with your actual secret)
WEBHOOK_SECRET = '123456'

# Verify the GitHub webhook signature
def verify_signature(request):
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return False
    
    sha_name, signature = signature.split('=')
    if sha_name != 'sha256':
        return False

    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=request.data, digestmod=hashlib.sha256)
    expected_signature = mac.hexdigest()

    return hmac.compare_digest(expected_signature, signature)

@app.route('/webhook', methods=['POST'])
def github_webhook():

    if not verify_signature(request):
        abort(403, 'Invalid signature')

    data = request.json
    action = data.get('action')
    sender = data.get('sender', {})
    ref = data.get('ref')
    pull_request = data.get('pull_request')
    timestamp = datetime.utcnow()

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

    print(event_data)

    if event_data:
        events_collection.insert_one(event_data)
        return jsonify({'message': 'Event saved'}), 201
    else:
        return jsonify({'message': 'Unsupported event'}), 400
    

# Serve the HTML UI
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'


# Fetch the latest events for UI (last 10 events)
@app.route('/events', methods=['GET'])
def get_events():
    events = list(events_collection.find().sort('timestamp', -1).limit(10))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
