from flask import Flask, request, jsonify
from pathlib import Path
from dotenv import load_dotenv
import os
import uuid
from flask_cors import CORS

# LangChain / Pinecone / Gemini
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone,ServerlessSpec
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import MongoDBChatMessageHistory

#importing the local files
from services.firebase import init_firebase, get_user_id_from_request
from services.file_upload import compute_file_hash,is_duplicate,record_upload

# Load .env variables (API keys)
load_dotenv()

# Flask app setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_URL")}}, supports_credentials=True)

#initialize firebase
init_firebase()

# Upload folder
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

# API keys
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["PINECONE_API_ENV"] = os.getenv("PINECONE_API_ENV", "us-east-1")

#index
index_name = os.getenv("PINECONE_INDEX_NAME")

#  Initialize LLM and embeddings
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# #pinecone db
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

#creating index run only once
# if index_name not in pc.list_indexes():
#      pc.create_index(
#                     name=index_name,
#                     dimension=768, 
#                     metric="cosine",
#                     spec=ServerlessSpec(cloud="aws", region="us-east-1") # Or PodSpec for dedicated clusters
#                 )


# Initialize vector store
vectorstore = PineconeVectorStore(index_name=index_name, embedding=gemini_embeddings)


# Load and chunk the file content
def data_loader_and_chunking(file_path,ext):
    if ext == "pdf":
        loader = PyMuPDFLoader(file_path)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        return text_splitter.split_documents(data) 
    else:
        print(f"Unsupported file extension: {ext}")
        raise ValueError(f"Unsupported file extension: {ext}")


@app.route("/")
def index():
    return "Flask app is running."


@app.route("/upload", methods=["POST"])
def upload_pdf():
    # Step 1: Get file from form-data
    uploaded_file = request.files.get("file")
    print(uploaded_file)
    
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400
    ext = uploaded_file.filename.split(".")[-1].lower()

    # Step 2: Read the file content into memory
    content = uploaded_file.read()

    # Step 3: Hash the file content to detect duplicates
    file_hash = compute_file_hash(content)

    if is_duplicate(file_hash):
         return jsonify({"message": "Duplicate file. Already uploaded."}), 400
    
    # Step 4: Save the file to disk
    file_path = UPLOAD_FOLDER / uploaded_file.filename
    file_path.write_bytes(content)


    try:
        chunks = data_loader_and_chunking(file_path,ext)
        PineconeVectorStore.from_documents(chunks, index_name=index_name, embedding=gemini_embeddings)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        file_path.unlink()

    record_upload(uploaded_file.filename, file_hash)
    return jsonify({"message": "File uploaded and indexed successfully.","chunks":len(chunks)})

@app.route("/chat", methods=["POST"])
def chat():
    # Authenticate user
    user_id = get_user_id_from_request()
    # print("userid:",user_id)
    data = request.get_json()
    query = data.get("query")
    chat_id = data.get("chatId")
        
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    # Generate chat_id if not provided
    if not chat_id:
        chat_id = str(uuid.uuid4())

    session_id = f"{user_id}:{chat_id}"

    #Use MongoDBChatMessageHistory
    chat_storage = MongoDBChatMessageHistory(
        connection_string=os.getenv("MONGO_URI"),
        session_id=session_id,
        database_name="assistant",
        collection_name="chats"
    )

    
    # Set up memory for chat context 
    memory = ConversationBufferMemory(memory_key="chat_history",chat_memory=chat_storage  , return_messages=True)

    # Conversational chain setup
    chain = ConversationalRetrievalChain.from_llm(
                llm=model,
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                memory=memory,
            )
    try:
        response = chain.invoke({"question": query})
        answer = response["answer"]
        # print(answer)
        return jsonify({"response": answer,"chatId":chat_id}),200
    except Exception as e:
        print("Chat error:", str(e))
        return jsonify({"error": "Failed to process query"}), 500

if __name__ == "__main__":
    app.run(debug=True)

