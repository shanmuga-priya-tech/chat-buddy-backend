from flask import request
import os
import firebase_admin
from firebase_admin import auth,credentials


def init_firebase():
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if FIREBASE_CREDENTIALS_PATH and os.path.exists(FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
    else:
        print("Warning: Firebase credentials not found. Authentication will be disabled.")
        firebase_admin.initialize_app()



def verify_firebase_token(id_token: str) -> str:
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid']
    except Exception as e:
        print(f"Firebase token verification failed: {e}")
        raise Exception("Invalid authentication token")

def get_user_id_from_request() -> str:
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise Exception("Missing or invalid Authorization header")
    
    id_token = auth_header.split('Bearer ')[1]
    return verify_firebase_token(id_token)
