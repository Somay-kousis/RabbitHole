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
    if os.environ.get("GROQ_API_KEY"):
        return "groq", "llama-3.3-70b-versatile"
    elif os.environ.get("GOOGLE_API_KEY"):
        return "google", "gemini-1.5-pro"
    elif os.environ.get("CEREBRAS_API_KEY"):
        return "cerebras", "llama3.1-70b"
    elif os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter", "meta-llama/llama-3.3-70b-instruct"
    elif os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY"):
        return "huggingface", "meta-llama/Llama-3.3-70B-Instruct"
    else:
        raise ValueError("No API keys found in environment variables to configure heavy LLM.")

def get_default_lite_provider():
    if os.environ.get("CEREBRAS_API_KEY"):
        return "cerebras", "llama3.1-8b"
    elif os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter", "google/gemma-2-9b-it:free"
    elif os.environ.get("GROQ_API_KEY"):
        return "groq", "llama-3.1-8b-instant"
    elif os.environ.get("GOOGLE_API_KEY"):
        return "google", "gemini-1.5-flash"
    elif os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY"):
        return "huggingface", "meta-llama/Llama-3.2-3B-Instruct"
    else:
        raise ValueError("No API keys found in environment variables to configure lite LLM.")

# Resolve defaults
def_heavy_prov, def_heavy_mod = get_default_heavy_provider()
def_lite_prov, def_lite_mod = get_default_lite_provider()

# 3. Dynamic Node Resolver Function
def resolve_node_model(var_name: str, temperature: float = 1.0):
    # Check for direct granular settings in .env (e.g. MODERATOR_PROVIDER / MODERATOR_MODEL)
    provider = os.environ.get(f"{var_name}_PROVIDER")
    model = os.environ.get(f"{var_name}_MODEL")
    
    # Determine Tier (LITE or HEAVY)
    is_lite = "LITE" in var_name or var_name in ["CONCLUSION", "RETRIVER_LITE"]
    
    if is_lite:
        tier_provider = os.environ.get("LITE_PROVIDER") or def_lite_prov
        tier_model = os.environ.get("LITE_MODEL") or def_lite_mod
    else:
        tier_provider = os.environ.get("HEAVY_PROVIDER") or def_heavy_prov
        tier_model = os.environ.get("HEAVY_MODEL") or def_heavy_mod
        
    final_provider = provider or tier_provider
    final_model = model or tier_model
    
    return create_llm(final_provider, final_model, temperature)

# 4. Final Node Models Assignment
MODERATOR_MODEL = resolve_node_model("MODERATOR")
SESSION_MODEL = resolve_node_model("SESSION")
JUDICIARY_MODEL = resolve_node_model("JUDICIARY")
RETRIEVER_MODEL = resolve_node_model("RETRIEVER")
QUERYREFINE_MODEL = resolve_node_model("QUERYREFINE")

# Even Perspectives: Defaults to Cerebras (Llama 3.1 70B & 8B)
PERSPECTIVE_MODEL_EVEN = resolve_node_model("PERSPECTIVE_MODEL_EVEN")
PERSPECTIVE_LITE_MODEL_EVEN = resolve_node_model("PERSPECTIVE_LITE_MODEL_EVEN")

# Odd Perspectives: Defaults to Google (Gemini 1.5 Flash) & OpenRouter/HuggingFace
# We explicitly override the defaults if no .env overrides exist:
odd_heavy_prov = "google" if os.environ.get("GOOGLE_API_KEY") else def_heavy_prov
odd_heavy_model = "gemini-1.5-flash" if os.environ.get("GOOGLE_API_KEY") else def_heavy_mod

odd_lite_prov = "openrouter" if os.environ.get("OPENROUTER_API_KEY") else ("huggingface" if (os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")) else def_lite_prov)
odd_lite_model = "google/gemma-2-9b-it:free" if os.environ.get("OPENROUTER_API_KEY") else ("meta-llama/Llama-3.2-3B-Instruct" if (os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")) else def_lite_mod)

PERSPECTIVE_MODEL_ODD = create_llm(
    os.environ.get("PERSPECTIVE_MODEL_ODD_PROVIDER") or odd_heavy_prov,
    os.environ.get("PERSPECTIVE_MODEL_ODD_MODEL") or odd_heavy_model
)
PERSPECTIVE_LITE_MODEL_ODD = create_llm(
    os.environ.get("PERSPECTIVE_LITE_MODEL_ODD_PROVIDER") or odd_lite_prov,
    os.environ.get("PERSPECTIVE_LITE_MODEL_ODD_MODEL") or odd_lite_model
)

JUDICIARY_LITE_MODEL = resolve_node_model("JUDICIARY_LITE")
QUERYREFINE_LITE_MODEL = resolve_node_model("QUERYREFINE_LITE")
CONCLUSION_MODEL = resolve_node_model("CONCLUSION")
RETRIVER_LITE_MODEL = resolve_node_model("RETRIVER_LITE")