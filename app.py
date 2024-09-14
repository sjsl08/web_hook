from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from bson.json_util import dumps

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb+srv://lallsimmu80:42JkKqQR9q115gKA@cluster0.h6oqq.mongodb.net')
db = client['github_webhook_db']
collection = db['events']

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    
    event_type = "UNKNOWN"
    event_data = {}
    
    # Handle push event
    if 'ref' in data and 'commits' in data:
        event_type = "PUSH"
        event_data = {
            "author": data['pusher']['name'],
            "to_branch": data['ref'].split('/')[-1],
            "commit_message": data['head_commit']['message'],
            "timestamp": datetime.now()
        }
    
    # Handle pull request event
    if 'pull_request' in data:  # Uncomment when handling pull request events
        event_type = "PULL_REQUEST"
        event_data = {
            "author": data['pull_request']['user']['login'],
            "from_branch": data['pull_request']['head']['ref'],
            "to_branch": data['pull_request']['base']['ref'],
            "timestamp": datetime.now()
        }
    
    # Handle merge event
    if 'merge' in data:  # Uncomment when handling merge events
        event_type = "MERGE"
        event_data = {
            "author": data['pull_request']['merged_by']['login'],
            "from_branch": data['pull_request']['head']['ref'],
            "to_branch": data['pull_request']['base']['ref'],
            "timestamp": datetime.now()
        }

    # Insert into MongoDB
    collection.insert_one({"event_type": event_type, **event_data})
    
    return jsonify({"message": "Webhook received"}), 200


# Serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# API to get events for the UI
@app.route('/get_events', methods=['GET'])
def get_events():
    events = list(collection.find().sort('timestamp', -1).limit(10))  # Get latest 10 events
    
    # Convert ObjectId to string
    for event in events:
        event['_id'] = str(event['_id'])
    
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
