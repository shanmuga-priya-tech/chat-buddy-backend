import hashlib
from services.mongo import uploads_collection

#hashing file to store in db
def compute_file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

# Check if file hash already exists
def is_duplicate(file_hash: str) -> bool:
    return uploads_collection.find_one({"file_hash": file_hash}) is not None

# Record file info in MongoDB
def record_upload(filename: str, file_hash: str):
    uploads_collection.insert_one({"filename": filename, "file_hash": file_hash})
