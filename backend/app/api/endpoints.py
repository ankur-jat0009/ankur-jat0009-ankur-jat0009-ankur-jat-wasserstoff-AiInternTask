from fastapi import APIRouter, UploadFile, File, Request
from backend.app.services.document_service import extract_text_from_pdf, extract_images_from_pdf
from backend.app.services.query_service import create_vector_store, search_similar_chunks
from backend.app.services.theme_service import synthesize_themes
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain_core.documents import Document
import os

router = APIRouter()

@router.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    os.makedirs("backend/data", exist_ok=True)
    file_path = f"backend/data/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Only process as PDF if file is PDF
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
        image_paths = extract_images_from_pdf(file_path)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        create_vector_store(chunks)
        return {"status": "uploaded", "chunks": len(chunks), "images": image_paths}
    elif file.content_type.startswith("image/"):
        img_save_path = f"backend/data/images/{file.filename}"
        os.makedirs("backend/data/images", exist_ok=True)
        with open(img_save_path, "wb") as img_f:
            img_f.write(open(file_path, "rb").read())
        return {"status": "image_uploaded", "image": img_save_path}
    else:
        return {"status": "unsupported file type"}

@router.post("/query/")
async def query_documents(request: Request):
    data = await request.json()
    question = data.get("question")
    history = data.get("history", [])

    # Combine chat history into a string for context
    history_context = ""
    for turn in history:
        if turn["role"] == "user":
            history_context += f"User: {turn['content']}\n"
        else:
            history_context += f"Bot: {turn['content']}\n"

    docs = search_similar_chunks(question)
    relevant_snippets = []
    citations = []
    doc_ids = []
    for idx, doc in enumerate(docs):
        relevant_snippets.append(doc.page_content)
        citations.append(f"Page: {doc.metadata.get('page', '')}, Para: {doc.metadata.get('paragraph', '')}")
        doc_ids.append(f"DOC{str(idx+1).zfill(3)}")
    context = "\n".join([f"{doc_ids[i]} ({citations[i]}): {relevant_snippets[i]}" for i in range(len(relevant_snippets))])

    prompt_template = """
    Conversation so far:
    {history}

    Using only the provided context, answer the question below.
    If the question refers to previous questions or answers, use the conversation history to resolve references.
    For each part of your answer, mention the document ID and page/para where the information was found.

    Context:
    {context}

    Question: {question}

    Answer (with document IDs and page/para citations):
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["history", "context", "question"])
    model = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0.3)
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    docs_for_chain = [Document(page_content=context)]
    response = chain(
        {"input_documents": docs_for_chain, "question": question, "history": history_context},
        return_only_outputs=True
    )
    return {"answer": response["output_text"]}