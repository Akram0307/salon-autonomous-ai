from flask import Flask, jsonify, request
from google.cloud import firestore
import logging


def create_app():
    app = Flask(__name__)

    logging.basicConfig(level=logging.INFO)
    try:
        db = firestore.Client()
        logging.info('Firestore client initialized')
    except Exception as e:
        logging.exception('Failed to init Firestore client: %s', e)
        db = None

    @app.route('/healthz', methods=['GET'])
    def healthz():
        return jsonify(status='healthy'), 200

    @app.route('/_healthz', methods=['GET'])
    def underscore_healthz():
        return jsonify(status='healthy'), 200

    @app.route('/readyz', methods=['GET'])
    def readyz():
        return jsonify(status='ready'), 200

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify(status='healthy'), 200

    @app.get('/api/services')
    def list_services():
        try:
            if db is None:
                return jsonify(services=[]), 200
            docs = db.collection('services').stream()
            items = []
            for d in docs:
                doc = d.to_dict() or {}
                doc['id'] = d.id
                items.append(doc)
            return jsonify(services=items), 200
        except Exception as e:
            logging.exception('Error listing services: %s', e)
            return jsonify(error='unavailable', detail=str(e)), 503

    @app.post('/api/services')
    def create_service():
        try:
            payload = request.get_json(silent=True) or {}
            name = payload.get('name')
            duration_min = payload.get('duration_min')
            price = payload.get('price')
            if not name or duration_min is None or price is None:
                return jsonify(error='bad_request', detail='name, duration_min, price required'), 400
            if db is None:
                return jsonify(error='unavailable', detail='Firestore not configured'), 503
            doc = {
                'name': str(name),
                'duration_min': int(duration_min),
                'price': float(price),
            }
            ref = db.collection('services').add(doc)[1]
            return jsonify(id=ref.id, **doc), 200
        except Exception as e:
            logging.exception('Error creating service: %s', e)
            return jsonify(error='unavailable', detail=str(e)), 503

    return app

app = create_app()
