from langchain_ollama import ChatOllama

MODERATOR_MODEL = ChatOllama(
    model="gemma4",
    temperature=1
)

PERSPECTIVE_MODEL = ChatOllama(
    model="qwen3.6",
    temperature=1
)

SESSION_MODEL = ChatOllama(
    model="gemma4",
    temperature=1
)

JUDICIARY_MODEL = ChatOllama(
    model="gemma4",
    temperature=1

)

QUERYREFINE_MODEL = ChatOllama(
    model="gemma4",
    temperature=1
)