from langchain_ollama import ChatOllama

MODERATOR_MODEL = ChatOllama(
    model="mistral",
    temperature=1
)

PERSPECTIVE_MODEL = ChatOllama(
    model="mistral",
    temperature=1
)

SESSION_MODEL = ChatOllama(
    model="mistral",
    temperature=1
)

JUDICIARY_MODEL = ChatOllama(
    model="phi4-mini",
    temperature=0.3
)

QUERYREFINE_MODEL = ChatOllama(
    model="phi4-mini",
    temperature=0
)

CONCLUSION_MODEL = ChatOllama(
    model="mistral",
    temperature=0.7
)