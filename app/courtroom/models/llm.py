import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama


load_dotenv()

MODEL_MODE = os.getenv("RABBITHOLE_MODEL_MODE", "local").lower()

LOCAL_DEFAULTS = {
    "MODERATOR": "gemma4",
    "PERSPECTIVE": "qwen3.6",
    "SESSION": "gemma4",
    "JUDICIARY": "gemma4",
    "QUERY_REFINE": "gemma4",
    "CONCLUSION": "qwen3.6",
}

REMOTE_DEFAULTS = {
    "MODERATOR": "llama-3.1-8b-instant",
    "PERSPECTIVE": "llama-3.3-70b-versatile",
    "SESSION": "llama-3.1-8b-instant",
    "JUDICIARY": "llama-3.3-70b-versatile",
    "QUERY_REFINE": "llama-3.1-8b-instant",
    "CONCLUSION": "llama-3.3-70b-versatile",
}


def model_name(role: str) -> str:
    if MODEL_MODE == "local":
        return os.getenv(f"LOCAL_{role}_MODEL", LOCAL_DEFAULTS[role])

    if MODEL_MODE == "remote":
        return os.getenv(f"REMOTE_{role}_MODEL", REMOTE_DEFAULTS[role])

    raise ValueError("RABBITHOLE_MODEL_MODE must be either 'local' or 'remote'.")


def build_model(role: str, temperature: float):
    if MODEL_MODE == "local":
        return ChatOllama(
            model=model_name(role),
            temperature=temperature,
        )

    if MODEL_MODE == "remote":
        from langchain_groq import ChatGroq

        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY is required when RABBITHOLE_MODEL_MODE=remote.")

        return ChatGroq(
            model=model_name(role),
            temperature=temperature,
        )

    raise ValueError("RABBITHOLE_MODEL_MODE must be either 'local' or 'remote'.")


MODERATOR_MODEL = build_model("MODERATOR", temperature=1)
PERSPECTIVE_MODEL = build_model("PERSPECTIVE", temperature=1)
SESSION_MODEL = build_model("SESSION", temperature=1)
JUDICIARY_MODEL = build_model("JUDICIARY", temperature=1)
QUERYREFINE_MODEL = build_model("QUERY_REFINE", temperature=1)
CONCLUSION_MODEL = build_model("CONCLUSION", temperature=0.7)
