# This file defines the data models used for storing document information and user queries.

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for declarative model definitions
Base = declarative_base()

# Document table model to store uploaded document metadata and content
class Document(Base):
    __tablename__ = 'documents'  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique identifier
    title = Column(String, index=True)                 # Document title or filename
    content = Column(Text)                             # Full text content of the document
    uploaded_by = Column(String)                       # Who uploaded the document (optional)
    upload_date = Column(String)                       # Date string when uploaded

# UserQuery table model to store each user query and its response
class UserQuery(Base):
    __tablename__ = 'user_queries'  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Unique identifier
    query_text = Column(Text)                           # User's question or query
    user_id = Column(Integer)                           # (Optional) ID of the user who asked
    document_id = Column(Integer)                       # Related document (Foreign key conceptually)
    response = Column(Text)                             # Bot's response to the query
    created_at = Column(String)                         # Timestamp when the query was made
