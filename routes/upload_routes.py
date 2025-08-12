from flask import Blueprint, request, jsonify
from pathlib import Path
from services.firebase import get_user_id_from_request
from helpers.file_upload import compute_file_hash, is_duplicate, record_upload
from components.loading_chunking import data_loader_and_chunking
from components.vectorstore import index_documents
from helpers.is_valid_pdf import is_valid_pdf

upload_bp = Blueprint("upload", __name__)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@upload_bp.route("/upload", methods=["POST"])
def upload_pdf():
    user_id = get_user_id_from_request()
    uploaded_file = request.files.get("file")

    # 1) Check if file is provided
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    # 2) Basic extension check
    if not uploaded_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    ext = uploaded_file.filename.split(".")[-1].lower()
    content = uploaded_file.read()

    # 3) File size check
    if len(content) > MAX_FILE_SIZE:
        return jsonify({"error": "File too large. Max size is 10 MB"}), 400

    # 4) check pdf signature
    if not is_valid_pdf(content):
        return jsonify({"error": "Invalid or corrupted PDF file."}), 400

    # 5) Compute file hash
    file_hash = compute_file_hash(content)

    # 6) Check duplicate for the same user
    if is_duplicate(file_hash):
        return jsonify({"message": "Duplicate file. Already uploaded."}), 400

    # 7) Save file temporarily
    file_path = UPLOAD_FOLDER / uploaded_file.filename
    file_path.write_bytes(content)

    #8) create namspace unique to  uploaded pdf
    namespace = f"{user_id}_{file_hash}"

    try:
        # 9) Load and chunk the file
        chunks = data_loader_and_chunking(file_path, ext)

        # 10) # Clean existing metadata: remove keys with empty string values and Prepare metadata for each chunk
        for doc in chunks:
            doc.metadata = {k: v for k, v in doc.metadata.items() if v != ""}
            doc.metadata["user_id"] = user_id
            doc.metadata["filename"] = uploaded_file.filename
            doc.metadata["namespace"] = namespace
                            
        # 11) Index into Pinecone with namespace
        index_documents(chunks,namespace=namespace)
        

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        file_path.unlink()

    # 12) Record the upload in MongoDB
    record_upload(user_id,uploaded_file.filename, file_hash,namespace)

    return jsonify({"message": "File uploaded and indexed successfully.", "chunks": len(chunks)})

