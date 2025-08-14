from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone,ServerlessSpec
from components.config import PINECONE_API_KEY, PINECONE_DATASET_INDEX

pc = Pinecone(api_key=PINECONE_API_KEY)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


#creating index run only once
# if PINECONE_DATASET_INDEX not in pc.list_indexes():
#      pc.create_index(
#                     name=PINECONE_DATASET_INDEX,
#                     dimension=768, 
#                     metric="cosine",
#                     spec=ServerlessSpec(cloud="aws", region="us-east-1") 
#                 )


def get_dataset_vectorstore():
    return PineconeVectorStore(index_name=PINECONE_DATASET_INDEX, embedding=embeddings)

def index_documents(documents):
    PineconeVectorStore.from_documents(documents, index_name=PINECONE_DATASET_INDEX, embedding=embeddings)
