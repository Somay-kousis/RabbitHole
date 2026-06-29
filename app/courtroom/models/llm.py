from dotenv import load_dotenv
load_dotenv()

import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models.openai import ChatOpenAI

# 1. LLM Client Factory
def create_llm(provider: str, model_name: str, temperature: float = 1.0):
    provider = provider.lower().strip()
    model_name = model_name.strip()
    
    if provider == "groq":
        return ChatGroq(model=model_name, temperature=temperature)
        
    elif provider == "google" or provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            temperature=temperature
        )
        
    elif provider == "cerebras":
        return ChatOpenAI(
            model=model_name,
            openai_api_key=os.environ.get("CEREBRAS_API_KEY"),
            openai_api_base="https://api.cerebras.ai/v1",
            temperature=temperature
        )
        
    elif provider == "openrouter":
        return ChatOpenAI(
            model=model_name,
            openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=temperature
        )
        
    elif provider == "huggingface":
        hf_key = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")
        return ChatOpenAI(
            model=model_name,
            openai_api_key=hf_key,
            openai_api_base="https://api-inference.huggingface.co/v1",
            temperature=temperature
        )
        
    else:
        raise ValueError(
            f"Unsupported provider '{provider}'. Must be one of: "
            "groq, google, gemini, cerebras, openrouter, huggingface"
        )

# 2. Smart Fallback Determinations (when .env configurations are absent)
def get_default_heavy_provider():
    if os.environ.get("CEREBRAS_API_KEY"):
        return "cerebras", "llama3.1-70b"
    elif os.environ.get("GROQ_API_KEY"):
        return "groq", "llama-3.3-70b-versatile"
    elif os.environ.get("GOOGLE_API_KEY"):
        return "google", "gemini-1.5-flash"
    elif os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter", "meta-llama/llama-3.3-70b-instruct"
    elif os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY"):
        return "huggingface", "meta-llama/Llama-3.3-70B-Instruct"
    else:
        raise ValueError("No API keys found in environment variables to configure heavy LLM.")

def get_default_lite_provider():
    if os.environ.get("CEREBRAS_API_KEY"):
        return "cerebras", "llama3.1-8b"
    elif os.environ.get("GOOGLE_API_KEY"):
        return "google", "gemini-1.5-flash"
    elif os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter", "google/gemma-2-9b-it:free"
    elif os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY"):
        return "huggingface", "meta-llama/Llama-3.2-3B-Instruct"
    elif os.environ.get("GROQ_API_KEY"):
        return "groq", "llama-3.3-70b-versatile"
    else:
        raise ValueError("No API keys found in environment variables to configure lite LLM.")

# Resolve defaults
def_heavy_prov, def_heavy_mod = get_default_heavy_provider()
def_lite_prov, def_lite_mod = get_default_lite_provider()

# 3. Fallback Wrapper Chat Model
class FallbackChatModel:
    """
    Wraps a list of LLM clients. If the primary client fails (e.g. 429 Rate Limit),
    it automatically falls back to the next model in the list.
    Supports structured output recursively across all fallback models.
    """
    def __init__(self, models):
        self.models = models

    def with_structured_output(self, schema, **kwargs):
        structured_models = [m.with_structured_output(schema, **kwargs) for m in self.models]
        if len(structured_models) == 1:
            return structured_models[0]
        return structured_models[0].with_fallbacks(structured_models[1:])

    def invoke(self, *args, **kwargs):
        if len(self.models) == 1:
            return self.models[0].invoke(*args, **kwargs)
        runnable = self.models[0].with_fallbacks(self.models[1:])
        return runnable.invoke(*args, **kwargs)

    def stream(self, *args, **kwargs):
        if len(self.models) == 1:
            return self.models[0].stream(*args, **kwargs)
        runnable = self.models[0].with_fallbacks(self.models[1:])
        return runnable.stream(*args, **kwargs)

    def batch(self, *args, **kwargs):
        if len(self.models) == 1:
            return self.models[0].batch(*args, **kwargs)
        runnable = self.models[0].with_fallbacks(self.models[1:])
        return runnable.batch(*args, **kwargs)

def build_fallback_chain(providers_and_models, temperature: float = 1.0):
    models = []
    for provider, model_name in providers_and_models:
        has_key = False
        if provider == "groq" and os.environ.get("GROQ_API_KEY"):
            has_key = True
        elif (provider in ["google", "gemini"]) and os.environ.get("GOOGLE_API_KEY"):
            has_key = True
        elif provider == "cerebras" and os.environ.get("CEREBRAS_API_KEY"):
            has_key = True
        elif provider == "openrouter" and os.environ.get("OPENROUTER_API_KEY"):
            has_key = True
        elif provider == "huggingface" and (os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")):
            has_key = True
            
        if has_key:
            try:
                models.append(create_llm(provider, model_name, temperature))
            except Exception:
                pass
                
    if not models:
        # Emergency fallback if no keys configured
        models.append(create_llm(def_lite_prov, def_lite_mod, temperature))
        
    return FallbackChatModel(models)

# 4. Final Fallback Model Chain Definitions
# Order: Low-limit free models first -> Medium limit -> OG models with massive limits at the bottom
MODERATOR_MODEL = build_fallback_chain([
    ("openrouter", "qwen/qwen-2.5-72b-instruct:free"),
    ("google", "gemini-1.5-flash"),
    ("cerebras", "llama3.1-70b"),
    ("groq", "llama-3.3-70b-versatile")
])

SESSION_MODEL = build_fallback_chain([
    ("openrouter", "qwen/qwen-2.5-72b-instruct:free"),
    ("google", "gemini-1.5-flash"),
    ("cerebras", "llama3.1-70b"),
    ("groq", "llama-3.3-70b-versatile")
])

JUDICIARY_MODEL = build_fallback_chain([
    ("openrouter", "qwen/qwen-2.5-72b-instruct:free"),
    ("google", "gemini-1.5-flash"),
    ("groq", "llama-3.3-70b-versatile"),
    ("cerebras", "llama3.1-70b")
])

RETRIEVER_MODEL = build_fallback_chain([
    ("openrouter", "qwen/qwen-2.5-72b-instruct:free"),
    ("google", "gemini-1.5-flash"),
    ("groq", "llama-3.3-70b-versatile"),
    ("cerebras", "llama3.1-70b")
])

QUERYREFINE_MODEL = build_fallback_chain([
    ("openrouter", "qwen/qwen-2.5-72b-instruct:free"),
    ("google", "gemini-1.5-flash"),
    ("cerebras", "llama3.1-70b"),
    ("groq", "llama-3.3-70b-versatile")
])

# Even Perspectives: Start on OpenRouter free -> Fallback HF -> Fallback Gemini -> Fallback Cerebras
PERSPECTIVE_MODEL_EVEN = build_fallback_chain([
    ("openrouter", "qwen/qwen-2.5-72b-instruct:free"),
    ("google", "gemini-1.5-flash"),
    ("cerebras", "llama3.1-70b")
])
PERSPECTIVE_LITE_MODEL_EVEN = build_fallback_chain([
    ("openrouter", "google/gemma-2-9b-it:free"),
    ("huggingface", "meta-llama/Llama-3.2-3B-Instruct"),
    ("google", "gemini-1.5-flash"),
    ("cerebras", "llama3.1-8b")
])

# Odd Perspectives: Start on Hugging Face -> Fallback OpenRouter -> Fallback Gemini -> Fallback Cerebras
PERSPECTIVE_MODEL_ODD = build_fallback_chain([
    ("google", "gemini-1.5-flash"),
    ("openrouter", "qwen/qwen-2.5-72b-instruct:free"),
    ("cerebras", "llama3.1-70b")
])
PERSPECTIVE_LITE_MODEL_ODD = build_fallback_chain([
    ("huggingface", "meta-llama/Llama-3.2-3B-Instruct"),
    ("openrouter", "google/gemma-2-9b-it:free"),
    ("google", "gemini-1.5-flash"),
    ("cerebras", "llama3.1-8b")
])

JUDICIARY_LITE_MODEL = build_fallback_chain([
    ("openrouter", "google/gemma-2-9b-it:free"),
    ("huggingface", "meta-llama/Llama-3.2-3B-Instruct"),
    ("google", "gemini-1.5-flash"),
    ("cerebras", "llama3.1-8b")
])

QUERYREFINE_LITE_MODEL = build_fallback_chain([
    ("openrouter", "google/gemma-2-9b-it:free"),
    ("huggingface", "meta-llama/Llama-3.2-3B-Instruct"),
    ("google", "gemini-1.5-flash"),
    ("cerebras", "llama3.1-8b")
])

CONCLUSION_MODEL = build_fallback_chain([
    ("openrouter", "google/gemma-2-9b-it:free"),
    ("huggingface", "meta-llama/Llama-3.2-3B-Instruct"),
    ("google", "gemini-1.5-flash"),
    ("cerebras", "llama3.1-8b")
])

RETRIVER_LITE_MODEL = build_fallback_chain([
    ("openrouter", "google/gemma-2-9b-it:free"),
    ("huggingface", "meta-llama/Llama-3.2-3B-Instruct"),
    ("google", "gemini-1.5-flash"),
    ("cerebras", "llama3.1-8b")
])