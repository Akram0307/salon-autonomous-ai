const admin = require('firebase-admin');

// Initialize Firebase Admin SDK
const serviceAccount = require('../../gcp-key.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseId: process.env.FIRESTORE_DATABASE_ID || 'salon-database'
});

const db = admin.firestore();

module.exports = { admin, db };
