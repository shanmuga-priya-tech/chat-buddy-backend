from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from components.config import PINECONE_API_KEY, PINECONE_INDEX_NAME



embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

pc = Pinecone(api_key=PINECONE_API_KEY)
def get_user_vectorstore(namespace):
    return PineconeVectorStore(index_name=PINECONE_INDEX_NAME, embedding=embeddings,namespace=namespace)

def index_documents(documents,namespace):
    PineconeVectorStore.from_documents(documents, index_name=PINECONE_INDEX_NAME, embedding=embeddings,namespace=namespace)
    