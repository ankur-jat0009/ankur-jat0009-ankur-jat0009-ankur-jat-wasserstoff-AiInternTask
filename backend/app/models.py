# This file defines the data models used for storing document information and user queries.

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    uploaded_by = Column(String)
    upload_date = Column(String)

class UserQuery(Base):
    __tablename__ = 'user_queries'

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text)
    user_id = Column(Integer)
    document_id = Column(Integer)  # Foreign key to the Document table
    response = Column(Text)  # The response generated for the query
    created_at = Column(String)  # Timestamp of when the query was made