from dotenv import load_dotenv
load_dotenv()

import os

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI


MODERATOR_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1
)

PERSPECTIVE_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1
)

PERSPECTIVE_LITE_MODEL = ChatGroq(
    model="gemma2-9b-it",
    temperature=1
)

SESSION_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1
)

JUDICIARY_LITE_MODEL = ChatGroq(
    model="gemma2-9b-it",
    temperature=1
)

JUDICIARY_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1
)

QUERYREFINE_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1
)

QUERYREFINE_LITE_MODEL = ChatGroq(
    model="gemma2-9b-it",
    temperature=1
)

CONCLUSION_MODEL = ChatGroq(
    model="gemma2-9b-it",
    temperature=1
)

RETRIEVER_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1
)

RETRIVER_LITE_MODEL = ChatGroq(
    model="gemma2-9b-it",
    temperature=1
)