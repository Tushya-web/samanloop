import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, auth

# ==================================================
# 🔐 Initialize Firebase Admin SDK (Railway Safe)
# ==================================================

if not firebase_admin._apps:

    # If running on Railway (env variables exist)
    if os.environ.get("FIREBASE_PRIVATE_KEY"):

        private_key = os.environ.get("FIREBASE_PRIVATE_KEY").replace("\\n", "\n")

        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": private_key,
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_CERT_URL"),
        })

    else:
        # Local development fallback
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(BASE_DIR, "serviceAccountKey.json")
        cred = credentials.Certificate(cred_path)

    firebase_admin.initialize_app(cred)

firebase_auth = auth

# ==================================================
# 🌍 Firebase Web API Key (Railway Variable)
# ==================================================

FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")


# ==================================================
# 🔐 Firebase Login
# ==================================================

def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    r = requests.post(url, json=payload)
    return r.json()


# ==================================================
# 📩 Send Verification Email (after register)
# ==================================================

def send_firebase_verification(idToken):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"

    payload = {
        "requestType": "VERIFY_EMAIL",
        "idToken": idToken
    }

    r = requests.post(url, json=payload)
    return r.json()


def send_firebase_verification_email(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"

    payload = {
        "requestType": "VERIFY_EMAIL",
        "email": email
    }

    return requests.post(url, json=payload)
