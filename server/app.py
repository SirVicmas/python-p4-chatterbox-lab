from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_as_text = False  # Change to avoid deprecated warning
CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    message_dict = [message.to_dict() for message in messages]
    response = make_response(jsonify(message_dict), 200)
    return response

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    body = data.get('body')
    username = data.get('username')
    
    if not body or not username:
        return jsonify({"error": "Both body and username are required"}), 400

    new_message = Message(body=body, username=username) 
    db.session.add(new_message)
    db.session.commit()
    response_message = new_message.to_dict()
    return jsonify(response_message), 201


@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
    
    data = request.get_json()
    updated_body = data.get('body')
    
    if updated_body is not None:
        message.body = updated_body
        db.session.commit()
        response_message = message.to_dict()
        return jsonify(response_message), 200
    else:
        return jsonify({"error": "No valid data provided for update"}), 400


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
    db.session.delete(message)
    db.session.commit()
    return jsonify({"message": "Message deleted successfully"})

if __name__ == '__main__':
    app.run(port=5555)
