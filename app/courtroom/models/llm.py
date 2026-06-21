from dotenv import load_dotenv
load_dotenv()

import os

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI


MODERATOR_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1
)

PERSPECTIVE_MODEL = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=1
)

SESSION_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1
)

JUDICIARY_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1
)

QUERYREFINE_MODEL = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=1
)

CONCLUSION_MODEL = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=1
)