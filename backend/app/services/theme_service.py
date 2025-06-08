from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_core.documents import Document

def synthesize_themes(answers, citations, question):
    prompt_template = """
    You are an expert document reader. Only extract the answer to the user's question from the provided context, with little bit summarizes with Document number and page number. 
    
    Context:
    {context}

    Question: {question}

    Answer:
    """
    # Combine answers and citations into context
    context = "\n".join([f"{c}: {a}" for a, c in zip(answers, citations)])
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    model = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0.3)
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    # Wrap context in a Document object for input_documents
    docs = [Document(page_content=context)]
    response = chain(
        {"input_documents": docs, "question": question},
        return_only_outputs=True
    )
    return response["output_text"]