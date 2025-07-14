from flask import Flask, request, jsonify
from Backend.Model import FirstLayerDMM  

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Jarvis Decision-Making API is running."})


@app.route('/classify', methods=['POST'])
def classify_query():
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({"error": "No 'message' provided in request."}), 400

        user_message = data['message']
        result = FirstLayerDMM(prompt=user_message)

        return jsonify({"tasks": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
