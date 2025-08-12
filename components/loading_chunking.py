from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def data_loader_and_chunking(file_path, ext):
    if ext == "pdf":
        loader = PyMuPDFLoader(file_path)
        data = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        return splitter.split_documents(data)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
