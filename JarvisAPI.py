from flask import Flask, request, jsonify
from Backend.Model import FirstLayerDMM  # Make sure this works after deployment

app = Flask(__name__)

# Health check endpoint
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Jarvis Decision-Making API is running."})


# Main Jarvis processing endpoint
@app.route('/run', methods=['POST'])
def run_jarvis():
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({"error": "No 'message' provided in request."}), 400

        user_message = data['message']

        # Call your model processing logic from FirstLayerDMM
        result = FirstLayerDMM(prompt=user_message)

        return jsonify({"response": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
