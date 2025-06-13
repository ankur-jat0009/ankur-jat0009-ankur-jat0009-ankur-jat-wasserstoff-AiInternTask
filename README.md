# FileBot 🤖 – Document Q\&A Chatbot

## Overview

**FileBot** is an AI-powered web application that lets you upload documents (PDFs, images, or text), ask questions about their content, and get instant, cited answers. It uses OCR to extract text from images, semantic search for relevant context, and LLMs for natural language responses.

---

## Features

* **Multi-format Upload:** Supports PDF, PNG, JPG, JPEG, and direct text input.
* **OCR Support:** Extracts text from scanned images and photos.
* **Natural Language Q\&A:** Ask questions and get answers from your documents.
* **Citations:** Answers include document IDs and context references.
* **Fast, User-Friendly Interface:** Simple upload and chat experience.
* **Theme Identification:** (Optional) Summarizes common themes across documents.

---

## Project Structure

```
AIintern/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   └── prompts.py
│   ├── data/
├── frontend/
│   └── app.py
├── .gitignore
├── main.py
├── requirements.txt
├── README.md
```

---

## Setup Instructions

```bash
# 1. Clone the Repository
git clone https://github.com/ankur-jat0009/ankur-jat-wasserstoff-AiInternTask.git
cd ankur-jat-wasserstoff-AiInternTask
```

```bash
# 2. Setup and Run Backend
python -m venv myenv
myenv\Scripts\activate     # On Windows
# Or for Mac/Linux: source myenv/bin/activate
pip install -r ../requirements.txt
uvicorn app.main:app --reload
```

```bash
# 3. Setup and Run Frontend
cd frontend
streamlit run app.py
```

---

## Usage

1. Open your browser and go to `http://localhost:8501` (Streamlit UI).
2. Upload PDFs, images, or paste text.
3. Ask questions about your uploaded documents.
4. View answers with citations.

---

## Deployment

You can deploy this project on platforms like **Render.com**, **Railway.app**, or **Hugging Face Spaces**.
See the deployment section in this README or open an issue for help.

---

## Contribution

Contributions are welcome!

* Fork the repo
* Create a feature branch
* Submit a pull request

---

**Made with ❤️ using FastAPI, Streamlit, PaddleOCR, and Gemini AI.**
