from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import string
import json
import os

app = Flask(__name__)
CORS(app)

DB_FILE = "tunnels.json"


if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def generate_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def save_tunnel(code, user_id, tunnel_type):
    with open(DB_FILE, "r") as f:
        db = json.load(f)
    db[code] = {
        "user_id": user_id,
        "type": tunnel_type,
        "used": False,
        "messages": []  
    }
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

@app.route("/generate_voice", methods=["POST"])
def generate_voice():
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    code = generate_code()
    save_tunnel(code, user_id, "voice")
    return jsonify({"code": code})

@app.route("/generate_message", methods=["POST"])
def generate_message():
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    code = generate_code()
    save_tunnel(code, user_id, "message")
    return jsonify({"code": code})

@app.route("/validate", methods=["POST"])
def validate_code():
    data = request.json
    code = data.get("code")
    if not code:
        return jsonify({"error": "Missing code"}), 400

    with open(DB_FILE, "r") as f:
        db = json.load(f)

    info = db.get(code)
    if not info:
        return jsonify({"valid": False, "reason": "Invalid code"})

    return jsonify({
        "valid": True,
        "user_id": info["user_id"],
        "type": info["type"]
    })
    
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    code = data.get("code")
    message = data.get("message")
    sender = data.get("sender", "web")  

    with open(DB_FILE, "r") as f:
        db = json.load(f)

    if code not in db:
        return jsonify({"error": "Invalid code"}), 400

  
    if "messages" not in db[code]:
        db[code]["messages"] = []

    db[code]["messages"].append({"from": sender, "content": message})

    with open(DB_FILE, "w") as f:
        json.dump(db, f)

    return jsonify({"status": "ok"})

@app.route("/get_messages", methods=["POST"])
def get_messages():
    data = request.json
    code = data.get("code")
    last = int(data.get("last", 0))

    with open(DB_FILE, "r") as f:
        db = json.load(f)

    if code not in db:
        return jsonify({"error": "Invalid code"}), 400

 
    if "messages" not in db[code]:
        db[code]["messages"] = []
        with open(DB_FILE, "w") as f:
            json.dump(db, f)

    all_messages = db[code]["messages"]
    new_messages = all_messages[last:]

    return jsonify({"messages": new_messages, "new_last": len(all_messages)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)