from dotenv import load_dotenv
load_dotenv()

import os
from langchain_groq import ChatGroq
from langchain_community.chat_models.openai import ChatOpenAI

# 1. API Key Detection and Provider Selection
CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if CEREBRAS_API_KEY:
    # Cerebras Provider (Blazing fast Llama 3.1 inference)
    print("Using Cerebras as the LLM provider.")
    heavy_llm = ChatOpenAI(
        model="llama3.1-70b",
        openai_api_key=CEREBRAS_API_KEY,
        openai_api_base="https://api.cerebras.ai/v1",
        temperature=1
    )
    lite_llm = ChatOpenAI(
        model="llama3.1-8b",
        openai_api_key=CEREBRAS_API_KEY,
        openai_api_base="https://api.cerebras.ai/v1",
        temperature=1
    )
elif OPENROUTER_API_KEY:
    # OpenRouter Provider (Free / Tiered Model routing)
    print("Using OpenRouter as the LLM provider.")
    heavy_llm = ChatOpenAI(
        model="meta-llama/llama-3.3-70b-instruct",
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=1
    )
    lite_llm = ChatOpenAI(
        model="google/gemma-2-9b-it:free",
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=1
    )
else:
    # Groq Fallback Provider (using GPT-OSS / Llama 3.3)
    print("Using Groq as the LLM provider.")
    heavy_llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=1
    )
    # Using llama-3.1-8b-instant until its August 2026 sunset, or fallback to gpt-oss-20b
    lite_llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=1
    )

# 2. Node Model Assignment
MODERATOR_MODEL = heavy_llm
PERSPECTIVE_MODEL = heavy_llm
SESSION_MODEL = heavy_llm
JUDICIARY_MODEL = heavy_llm
RETRIEVER_MODEL = heavy_llm
QUERYREFINE_MODEL = heavy_llm

PERSPECTIVE_LITE_MODEL = lite_llm
JUDICIARY_LITE_MODEL = lite_llm
QUERYREFINE_LITE_MODEL = lite_llm
CONCLUSION_MODEL = lite_llm
RETRIVER_LITE_MODEL = lite_llm