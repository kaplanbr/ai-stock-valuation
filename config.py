
import streamlit as st
import os

# Try loading from Streamlit secrets first
try:
    # Use dict access to ensure it loads, use .get() to avoid key errors
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") 

# Fallback: If running locally without Streamlit context (e.g., debugging logic)
except (FileNotFoundError, AttributeError):

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")