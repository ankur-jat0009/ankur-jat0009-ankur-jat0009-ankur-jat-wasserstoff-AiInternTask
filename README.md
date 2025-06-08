# Chatbot Theme Identifier

## Overview
The Chatbot Theme Identifier is a web-based application designed to facilitate document analysis and question answering. Users can upload a variety of document types, ask questions about their content, and receive accurate answers with citations. The application also identifies and summarizes common themes across all uploaded documents based on user queries.

## Features
- **Document Upload**: Users can upload 75+ documents in formats such as PDF, images, and text files.
- **Text Extraction**: The application extracts text from documents, including OCR capabilities for scanned images.
- **Natural Language Querying**: Users can submit questions in natural language and receive relevant answers.
- **Citations**: Each answer is accompanied by clear citations indicating the document ID, page, and paragraph.
- **Theme Identification**: The application analyzes responses to identify and summarize common themes across documents.
- **User-Friendly Interface**: A simple web interface allows for easy navigation and interaction.

## Project Structure
The project is organized into two main directories: `backend` and `frontend`.

### Backend
- **app**: Contains the core application logic, including API endpoints, services, models, and configuration.
- **data**: Stores uploaded documents and processed data.
- **Dockerfile**: Instructions for building a Docker image for the backend application.
- **requirements.txt**: Lists the Python dependencies required for the backend.

### Frontend
- **public**: Contains static assets for the frontend application.
- **src**: Contains the main React application code, including components and pages.
- **package.json**: Configuration file for npm, listing dependencies and scripts.
- **tsconfig.json**: TypeScript configuration file.

## Setup Instructions
1. **Clone the Repository**: 
   ```
   git clone <repository-url>
   cd chatbot_theme_identifier
   ```

2. **Backend Setup**:
   - Navigate to the `backend` directory.
   - Create a virtual environment and activate it.
   - Install dependencies:
     ```
     pip install -r requirements.txt
     ```
   - Run the backend server:
     ```
     uvicorn app.main:app --reload
     ```

3. **Frontend Setup**:
   - Navigate to the `frontend` directory.
   - Install dependencies:
     ```
     npm install
     ```
   - Start the frontend application:
     ```
     npm start
     ```

## Usage
- Access the application through your web browser at `http://localhost:3000`.
- Upload documents using the provided interface.
- Ask questions related to the content of the uploaded documents.
- Review the answers and themes identified by the chatbot.

## Contribution
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.