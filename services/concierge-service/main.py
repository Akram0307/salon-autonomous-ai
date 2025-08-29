from flask import Flask, jsonify, request
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def hello_world():
    logging.info('Concierge service root accessed.')
    return 'Hello from Concierge Service!'

@app.route('/health')
def health_check():
    logging.info('Concierge service health check accessed.')
    return jsonify({'status': 'ok', 'service': 'concierge-service'})

# Example route for handling WhatsApp messages (placeholder)
@app.route('/whatsapp', methods=['POST'])
def handle_whatsapp():
    logging.info('WhatsApp webhook received.')
    data = request.json
    # Process WhatsApp message here
    logging.info(f'Received WhatsApp data: {data}')
    return jsonify({'status': 'received', 'message': 'WhatsApp message processed'})

# Example route for handling GMB messages (placeholder)
@app.route('/gmb', methods=['POST'])
def handle_gmb():
    logging.info('GMB webhook received.')
    data = request.json
    # Process GMB message here
    logging.info(f'Received GMB data: {data}')
    return jsonify({'status': 'received', 'message': 'GMB message processed'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
