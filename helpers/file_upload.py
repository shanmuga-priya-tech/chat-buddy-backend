import hashlib
from services.mongo import dataset_collection

#hashing file to store in db
def compute_file_hash(content):
    return hashlib.sha256(content).hexdigest()

# Check if file hash already exists
def is_duplicate(file_hash):
    return dataset_collection.find_one({"file_hash": file_hash}) is not None

# Record file info in MongoDB
def record_upload(filename, file_hash, uploaded_at):
    return dataset_collection.insert_one({"filename": filename, "file_hash": file_hash,"uploaded_at":uploaded_at})
