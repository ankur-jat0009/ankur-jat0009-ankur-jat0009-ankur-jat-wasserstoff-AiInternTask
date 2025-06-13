# Required libraries for routing and request handling
from fastapi import APIRouter, UploadFile, File, Request
from backend.app.services.document_service import extract_text_from_pdf
from backend.app.services.query_service import create_vector_store, search_sequential_chunks
from backend.app.core.ocr_utils import ocr_image
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain_core.documents import Document
import os, uuid, shutil
from fastapi import FastAPI
from backend.app.api.endpoints import router

app = FastAPI()

app.include_router(router)

# Create a router instance for FastAPI routes
router = APIRouter()

# State for assigning unique document IDs
DOC_COUNTER = 1
DOC_ID_MAP = {}

# Utility to assign a DOC ID to each uploaded file
def get_next_doc_id(filename):
    global DOC_COUNTER
    if filename not in DOC_ID_MAP:
        DOC_ID_MAP[filename] = f"DOC{DOC_COUNTER}"
        DOC_COUNTER += 1
    return DOC_ID_MAP[filename]

# Backend reset route: deletes files and vector index
@router.post("/reset_backend/")
async def reset_backend():
    data_folder = "backend/data"
    if os.path.exists(data_folder):
        shutil.rmtree(data_folder)
    os.makedirs(data_folder, exist_ok=True)

    faiss_index_folder = "faiss_index"
    if os.path.exists(faiss_index_folder):
        shutil.rmtree(faiss_index_folder)

    global DOC_COUNTER, DOC_ID_MAP
    DOC_COUNTER = 1
    DOC_ID_MAP = {}

    return {"status": "success", "message": "Backend reset: all uploaded data and indexes deleted."}

# Document upload route (PDFs and images)
@router.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    os.makedirs("backend/data", exist_ok=True)
    file_path = f"backend/data/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    doc_id = get_next_doc_id(file.filename)

    # Handling PDF files
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=50000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        if not chunks or all([not c.strip() for c in chunks]):
            return {"status": "error", "message": "No text found in document."}
        page_mapping = {i: 1 for i in range(len(chunks))}  # Simplified to 1-page mapping
        create_vector_store(chunks, doc_id, page_mapping)

        return {"status": "uploaded", "doc_id": doc_id, "chunks": len(chunks)}

    # Handling image files (OCR)
    elif file.content_type.startswith("image/"):
        os.makedirs("backend/data/images", exist_ok=True)
        img_save_path = f"backend/data/images/{file.filename}"
        with open(img_save_path, "wb") as img_f:
            img_f.write(await file.read())

        text = ocr_image(img_save_path)
        print(f"OCR extracted text: {text}")
        if not text.strip():
            return {"status": "error", "message": "No text found in image."}
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        if not chunks or all([not c.strip() for c in chunks]):
            return {"status": "error", "message": "No text found in image."}
        page_mapping = {i: 1 for i in range(len(chunks))}
        create_vector_store(chunks, doc_id, page_mapping)

        return {"status": "image_uploaded", "doc_id": doc_id, "chunks": len(chunks)}

    return {"status": "unsupported file type"}

# Raw text upload route
@router.post("/upload_text/")
async def upload_text(data: dict):
    text = data.get("text", "")
    if not text.strip():
        return {"status": "error", "message": "No text provided."}
    doc_id = get_next_doc_id(f"text_{uuid.uuid4().hex[:8]}")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    if not chunks or all([not c.strip() for c in chunks]):
        return {"status": "error", "message": "No valid text found."}
    page_mapping = {i: 1 for i in range(len(chunks))}
    create_vector_store(chunks, doc_id, page_mapping)

    return {"status": "uploaded", "doc_id": doc_id, "chunks": len(chunks)}

# Query processing route
@router.post("/query/")
async def query_documents(request: Request):
    data = await request.json()
    question = data.get("question")
    history = data.get("history", [])

    # Format chat history into a single string
    history_context = "\n".join(
        [f"{turn['role'].capitalize()}: {turn['content']}" for turn in history]
    )

    # Search for the most relevant document chunk
    docs, _ = search_sequential_chunks(question)
    if not docs:
        return {"answer": "Sorry, I couldn't find that in the documents."}

    relevant_snippets, doc_ids = [], []
    for idx, doc in enumerate(docs):
        relevant_snippets.append(doc.page_content)
        doc_ids.append(doc.metadata.get("doc_id", f"DOC{idx+1}"))

    # Combine all relevant chunk contents into a single context
    context = "\n".join([
        f"{doc_ids[i]}: {relevant_snippets[i]}"
        for i in range(len(relevant_snippets))
    ])

    # Prompt setup for Gemini with conversational tone
    prompt_template = """
    You are a helpful AI assistant. Answer the question as detailed as possible from the provided context in a natural, conversational way.
    After giving the answer from the document, add any extra helpful information you know about the topic.
    If the answer is not found, say: "Sorry, I couldn't find that in the documents."
    Only use the document ID (e.g., DOC1, DOC2) for citations.

    Context:
    {context}

    User's Question: {question}

    Your Answer:
    """

    # Load LangChain prompt with input variables
    prompt = PromptTemplate(template=prompt_template, input_variables=["history", "context", "question"])
    model = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0.3)
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    docs_for_chain = [Document(page_content=context)]

    # Run the model with provided context and return the answer
    response = chain(
        {"input_documents": docs_for_chain, "question": question, "history": history_context},
        return_only_outputs=True
    )
    answer = response["output_text"]
    return {"answer": answer}
