# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

# Import LangChain tools for embeddings and vector search
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

import uuid
import json
from backend.app.prompts import CHAT_PROMPT_TEMPLATE  # Externalized prompt template

# Paths for saving vector index and metadata
VECTOR_STORE_PATH = "faiss_index"
METADATA_PATH = "vector_metadata.json"

# Load previously saved metadata (doc_id -> page mapping)
def load_metadata():
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r") as f:
            return json.load(f)
    return {}

# Save metadata (used after creating new vector store)
def save_metadata(metadata):
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f)

# Create or update a FAISS vector store using new text chunks
def create_vector_store(text_chunks, doc_id, page_mapping):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    metadata_store = load_metadata()

    # Attach metadata (doc_id, page number, paragraph number, and source type)
    new_docs = [
        Document(
            page_content=chunk,
            metadata={
                "doc_id": doc_id,
                "page": page_mapping.get(i, 1),
                "paragraph": i + 1,
                "source": "image" if "image_doc" in doc_id or doc_id.lower().startswith("img") else "pdf"
            }
        )
        for i, chunk in enumerate(text_chunks)
    ]

    # Load existing index or create new one
    if os.path.exists(f"{VECTOR_STORE_PATH}/index.faiss"):
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        vector_store.add_documents(new_docs)
    else:
        vector_store = FAISS.from_documents(new_docs, embedding=embeddings)

    # Save the updated vector store and associated metadata
    vector_store.save_local(VECTOR_STORE_PATH)
    metadata_store[doc_id] = {"pages": page_mapping}
    save_metadata(metadata_store)

# Semantic search: returns top-k most similar document chunks
def search_similar_chunks(query):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    try:
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    except Exception:
        return []
    docs = vector_store.similarity_search(query, k=15)
    return docs

# Sequential search for answering: returns only top-1 result
def search_sequential_chunks(query):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    try:
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    except Exception:
        return [], []
    docs = vector_store.similarity_search(query, k=3)
    if docs:
        return [docs[0]], []
    return [], []

# Generates the final answer using Gemini and document context
def run_prompt_with_context(question, context, history_context=""):
    from langchain.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.chains.question_answering import load_qa_chain
    from langchain_core.documents import Document

    # Load prompt template and inject context, question, and history
    prompt = PromptTemplate(
        template=CHAT_PROMPT_TEMPLATE,
        input_variables=["history", "context", "question"]
    )

    # Load Gemini model (2.0 Flash) and QA chain
    model = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0.3)
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    # Inject the context chunk into a LangChain document wrapper
    docs_for_chain = [Document(page_content=context)]

    # Ask question using the LLM + retrieved context
    response = chain(
        {"input_documents": docs_for_chain, "question": question, "history": history_context},
        return_only_outputs=True
    )
    return response["output_text"]
