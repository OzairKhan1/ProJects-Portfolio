from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Load token
with open("token.txt") as t:
    API_TOKEN = t.read().strip()

@app.route('/get_data/<system_id>', methods=['GET'])
def get_data(system_id):
    token = request.headers.get("X-Auth-Token")
    if token != API_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        with open("today_data.json") as f:
            data_map = json.load(f)
        data = data_map.get(system_id, "No data assigned")
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This block is only used for manual testing (not triggered when using Gunicorn)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
