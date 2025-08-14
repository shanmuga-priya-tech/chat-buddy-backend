from pymongo import MongoClient
from components.config import MONGO_URI

# Create one global client & db instance
client = MongoClient(MONGO_URI)
db = client["assistant"]
chat_collection = db["chats"]
dataset_collection = db["dataset"]
uploads_collection = db["uploads"]



