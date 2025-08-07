from flask import Blueprint
from google.cloud import firestore
from google.oauth2 import service_account
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard Cloud Run secret mount path
SECRET_PATH = '/secrets/booking-service-key/1'

try:
    logger.info(f"Initializing Firestore client with secret path: {SECRET_PATH}")
    if os.path.exists(SECRET_PATH):
        credentials = service_account.Credentials.from_service_account_file(SECRET_PATH)
        db = firestore.Client(credentials=credentials)
        logger.info("Firestore client initialized successfully")
    else:
        logger.error(f"Secret file not found at: {SECRET_PATH}")
        raise RuntimeError("Secret file not found")
except Exception as e:
    logger.error(f"Failed to initialize Firestore client: {str(e)}")
    raise

bp = Blueprint('services', __name__, url_prefix='/services')

@bp.route('/health')
def health():
    logger.info("Health check endpoint called")
    return {'status': 'ok'}
