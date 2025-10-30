# config.py
import os

# Try to load from Streamlit Secrets (cloud)
try:
    import streamlit as st
    if "OPENAI_API_KEY" in st.secrets:
        OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
        DATABASE_URL = st.secrets["DATABASE_URL"]
    else:
        raise KeyError("Not running in Streamlit or secrets not set")
except (ImportError, KeyError):
    # Fallback to .env (local development)
    from dotenv import load_dotenv
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")

# Validate
if not OPENAI_API_KEY:
    raise EnvironmentError("Missing OPENAI_API_KEY")
if not DATABASE_URL:
    raise EnvironmentError("Missing DATABASE_URL")