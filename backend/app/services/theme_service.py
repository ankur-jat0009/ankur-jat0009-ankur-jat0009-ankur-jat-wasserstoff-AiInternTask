# Import Gemini model and LangChain utilities
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_core.documents import Document

# Synthesizes common themes across multiple answers using Gemini
def synthesize_themes(answers, citations, question):
    # Prompt instructs the model to extract themes from multiple document-based answers
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

    # Combine all individual answers and their citations into a unified context string
    context = "\n".join([f"{c}: {a}" for a, c in zip(answers, citations)])

    # Inject the context and question into the prompt
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    # Initialize Gemini model
    model = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0.3)

    # Use QA chain to feed prompt and context
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    docs = [Document(page_content=context)]

    # Execute the chain and return the thematic summary
    response = chain(
        {"input_documents": docs, "question": question},
        return_only_outputs=True
    )
    return response["output_text"]
