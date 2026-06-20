from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq

MODERATOR_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1
)

PERSPECTIVE_MODEL = ChatGroq(
    model="llama-3.3-70b-versatile",
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
    temperature=0.7
)