from dotenv import load_dotenv
load_dotenv()

import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable


# Helper: Cerebras key supports both spellings (CEREBRAS vs CEREBAS typo in .env)
def _get_cerebras_key():
    return os.environ.get("CEREBRAS_API_KEY") or os.environ.get("CEREBAS_API_KEY")

# Helper: SambaNova key
def _get_sambanova_key():
    return os.environ.get("SAMBANOVA_API_KEY")


# 1. LLM Client Factory
def create_llm(provider: str, model_name: str, temperature: float = 1.0):
    provider = provider.lower().strip()
    model_name = model_name.strip()

    if provider == "groq":
        return ChatGroq(model=model_name, temperature=temperature)

    elif provider in ("google", "gemini"):
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            temperature=temperature
        )

    elif provider == "cerebras":
        return ChatOpenAI(
            model=model_name,
            openai_api_key=_get_cerebras_key(),
            openai_api_base="https://api.cerebras.ai/v1",
            temperature=temperature
        )

    elif provider == "sambanova":
        return ChatOpenAI(
            model=model_name,
            openai_api_key=_get_sambanova_key(),
            openai_api_base="https://api.sambanova.ai/v1",
            temperature=temperature,
            max_retries=0
        )

    elif provider == "openrouter":
        return ChatOpenAI(
            model=model_name,
            openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_retries=0
        )

    else:
        raise ValueError(
            f"Unsupported provider '{provider}'. Must be one of: "
            "groq, google, gemini, cerebras, sambanova, openrouter"
        )


# 2. Smart Fallback Determinations (when .env configurations are absent)
def get_default_heavy_provider():
    if os.environ.get("GROQ_API_KEY"):
        return "groq", "llama-3.3-70b-versatile"
    elif _get_cerebras_key():
        return "cerebras", "llama-3.3-70b"
    elif _get_sambanova_key():
        return "sambanova", "Meta-Llama-3.3-70B-Instruct"
    elif os.environ.get("GOOGLE_API_KEY"):
        return "google", "gemini-2.5-flash"
    else:
        raise ValueError("No API keys found in environment variables to configure heavy LLM.")

def get_default_lite_provider():
    if os.environ.get("GROQ_API_KEY"):
        return "groq", "llama-3.1-8b-instant"
    elif _get_cerebras_key():
        return "cerebras", "llama-3.1-8b"
    elif _get_sambanova_key():
        return "sambanova", "Meta-Llama-3.1-8B-Instruct"
    elif os.environ.get("GOOGLE_API_KEY"):
        return "google", "gemini-2.5-flash"
    else:
        raise ValueError("No API keys found in environment variables to configure lite LLM.")


# Resolve defaults
def_heavy_prov, def_heavy_mod = get_default_heavy_provider()
def_lite_prov, def_lite_mod = get_default_lite_provider()


# 3. Fallback Wrapper Chat Model
class FallbackChatModel(Runnable):
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
        elif provider in ("google", "gemini") and os.environ.get("GOOGLE_API_KEY"):
            has_key = True
        elif provider == "cerebras" and _get_cerebras_key():
            has_key = True
        elif provider == "sambanova" and _get_sambanova_key():
            has_key = True
        elif provider == "openrouter" and os.environ.get("OPENROUTER_API_KEY"):
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


# 4. Fallback Chain Definitions
# Staggered provider order to distribute load across parallel nodes.
# Heavy models: 70B class for synthesis, moderation, judiciary
# Lite models: 8B class for grading, filtering, simple decisions

# Default chains: Groq first (used by sequential nodes like moderator, judiciary)
HEAVY = [
    ("groq",      "llama-3.3-70b-versatile"),
    ("cerebras",  "llama-3.3-70b"),
    ("sambanova", "Meta-Llama-3.3-70B-Instruct"),
    ("google",    "gemini-2.5-flash"),
]

LITE = [
    ("groq",      "llama-3.1-8b-instant"),
    ("cerebras",  "llama-3.1-8b"),
    ("sambanova", "Meta-Llama-3.1-8B-Instruct"),
    ("google",    "gemini-2.5-flash"),
]

# Staggered chains for parallel perspective nodes to avoid rate limit collisions
HEAVY_EVEN = [
    ("cerebras",  "llama-3.3-70b"),
    ("sambanova", "Meta-Llama-3.3-70B-Instruct"),
    ("groq",      "llama-3.3-70b-versatile"),
    ("google",    "gemini-2.5-flash"),
]

HEAVY_ODD = [
    ("sambanova", "Meta-Llama-3.3-70B-Instruct"),
    ("groq",      "llama-3.3-70b-versatile"),
    ("cerebras",  "llama-3.3-70b"),
    ("google",    "gemini-2.5-flash"),
]

LITE_EVEN = [
    ("cerebras",  "llama-3.1-8b"),
    ("sambanova", "Meta-Llama-3.1-8B-Instruct"),
    ("groq",      "llama-3.1-8b-instant"),
    ("google",    "gemini-2.5-flash"),
]

LITE_ODD = [
    ("sambanova", "Meta-Llama-3.1-8B-Instruct"),
    ("groq",      "llama-3.1-8b-instant"),
    ("cerebras",  "llama-3.1-8b"),
    ("google",    "gemini-2.5-flash"),
]

MODERATOR_MODEL        = build_fallback_chain(HEAVY)
SESSION_MODEL          = build_fallback_chain(HEAVY)
JUDICIARY_MODEL        = build_fallback_chain(HEAVY)
RETRIEVER_MODEL        = build_fallback_chain(HEAVY)
QUERYREFINE_MODEL      = build_fallback_chain(HEAVY)
PERSPECTIVE_MODEL_EVEN = build_fallback_chain(HEAVY_EVEN)
PERSPECTIVE_MODEL_ODD  = build_fallback_chain(HEAVY_ODD)

PERSPECTIVE_LITE_MODEL_EVEN = build_fallback_chain(LITE_EVEN)
PERSPECTIVE_LITE_MODEL_ODD  = build_fallback_chain(LITE_ODD)
JUDICIARY_LITE_MODEL        = build_fallback_chain(LITE)
QUERYREFINE_LITE_MODEL      = build_fallback_chain(LITE)
CONCLUSION_MODEL            = build_fallback_chain(LITE)
RETRIVER_LITE_MODEL         = build_fallback_chain(LITE)