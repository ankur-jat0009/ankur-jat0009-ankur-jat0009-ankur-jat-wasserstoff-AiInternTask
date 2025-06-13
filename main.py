# Load environment variables from a .env file
from dotenv import load_dotenv
import os

# Load all variables from .env into the environment
load_dotenv()

# Set the Google API key from the loaded environment variables
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# FastAPI application setup
from fastapi import FastAPI
from backend.app.api.endpoints import router  # Import API routes from your endpoints module

# Create a FastAPI app instance
app = FastAPI()

# Register the router containing all endpoints (upload, query, reset, etc.)
app.include_router(router)
