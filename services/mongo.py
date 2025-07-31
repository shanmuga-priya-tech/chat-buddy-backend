import os
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))

# Select database and collections
db = client["assistant"]
uploads_collection = db["uploads"]

