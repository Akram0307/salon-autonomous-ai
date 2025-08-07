from flask import Flask, jsonify
import os
from .api_services import bp as services_bp

app = Flask(__name__)
app.register_blueprint(services_bp)

@app.route('/health')
def health():
    return jsonify(status='ok'), 200

@app.route('/')
def hello_world():
    return jsonify(message='Hello from booking-service!')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
