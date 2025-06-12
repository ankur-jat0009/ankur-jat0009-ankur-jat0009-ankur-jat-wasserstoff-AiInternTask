from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_core.documents import Document

def synthesize_themes(answers, citations, question):
    prompt_template = """
    You are an expert analyst. You are given a user's question and multiple document-based answers with their citations.

    Your job is to:
    1. Identify and summarize common themes across these answers.
    2. Mention supporting document IDs for each theme (no page numbers).
    3. If there is no valid content to answer the question, respond with: "Answer not found in documents."

    Question: {question}

    Answers with citations:
    {context}

    Thematic Summary:
    """

    # Combine answers and citations into context
    context = "\n".join([f"{c}: {a}" for a, c in zip(answers, citations)])
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    model = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0.3)
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    docs = [Document(page_content=context)]

    response = chain(
        {"input_documents": docs, "question": question},
        return_only_outputs=True
    )
    return response["output_text"]