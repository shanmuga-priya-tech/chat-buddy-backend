import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_API_ENV = os.getenv("PINECONE_API_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
MONGO_URI = os.getenv("MONGO_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL")


os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["PINECONE_API_ENV"] = PINECONE_API_ENV
