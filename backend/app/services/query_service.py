from dotenv import load_dotenv
import os

load_dotenv()
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

def create_vector_store(text_chunks):
    """
    Create and save a FAISS vector store from text chunks.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def search_similar_chunks(query):
    """
    Load the FAISS vector store and perform a similarity search for the query.
    Returns a list of matching document chunks.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = vector_store.similarity_search(query)
    return docs