import hashlib
from services.mongo import uploads_collection

#hashing file to store in db
def compute_file_hash(content):
    return hashlib.sha256(content).hexdigest()

# Check if file hash already exists
def is_duplicate(file_hash):
    return uploads_collection.find_one({"file_hash": file_hash}) is not None

# Record file info in MongoDB
def record_upload(userid, filename, file_hash, namespace):
    return uploads_collection.insert_one({"userid":userid,"filename": filename, "file_hash": file_hash,"namespace":namespace})
