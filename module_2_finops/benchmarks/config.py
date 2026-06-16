"""
Shared config for all benchmarks.
Reads model routing and API settings from .env
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── Model routing (cross-provider) ────────────────────────────────────────────

@dataclass
class ModelConfig:
    simple:   str
    moderate: str
    complex:  str
    default:  str

MODELS = ModelConfig(
    simple   = os.getenv("MODEL_SIMPLE",   "mistral/mistral-small-latest"),
    moderate = os.getenv("MODEL_MODERATE", "deepseek/deepseek-chat"),
    complex  = os.getenv("MODEL_COMPLEX",  "mistral/mistral-large-latest"),
    default  = os.getenv("MODEL_DEFAULT",  "mistral/mistral-small-latest"),
)

# ── LiteLLM client ────────────────────────────────────────────────────────────

LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
LITELLM_API_KEY  = os.getenv("LITELLM_API_KEY",  "sk-litellm-master-2026")

client = OpenAI(
    base_url=f"{LITELLM_BASE_URL}/v1",
    api_key=LITELLM_API_KEY,
)

# ── Projections ───────────────────────────────────────────────────────────────

MONTHLY_CALLS         = int(os.getenv("MONTHLY_CALLS",        "500000"))
DAILY_CALLS           = int(os.getenv("DAILY_CALLS",          "100000"))
DAILY_CONVERSATIONS   = int(os.getenv("DAILY_CONVERSATIONS",  "10000"))

# ── Pricing table ($/1K tokens) ───────────────────────────────────────────────
# Add your models here as you test new providers.

PRICING: dict[str, dict] = {
    # Mistral
    "mistral/mistral-small-latest":  {"input": 0.0001,  "output": 0.0003},
    "mistral/mistral-large-latest":  {"input": 0.002,   "output": 0.006},
    # DeepSeek
    "deepseek/deepseek-chat":        {"input": 0.00027, "output": 0.0011},
    "deepseek/deepseek-reasoner":    {"input": 0.0014,  "output": 0.0055},
    # Gemini
    "gemini/gemini-2.0-flash":       {"input": 0.0001,  "output": 0.0004},
    "gemini/gemini-1.5-pro":         {"input": 0.00125, "output": 0.005},
    # Claude
    "claude-haiku":                  {"input": 0.00025, "output": 0.00125},
    "claude-sonnet":                 {"input": 0.003,   "output": 0.015},
    "claude-opus":                   {"input": 0.015,   "output": 0.075},
    # OpenAI
    "gpt-4o-mini":                   {"input": 0.00015, "output": 0.0006},
    "gpt-4o":                        {"input": 0.0025,  "output": 0.01},
    # Groq
    "groq/llama-3.3-70b":            {"input": 0.00006, "output": 0.00006},
}

def token_cost(model: str, input_tokens: int, output_tokens: int = 0) -> float:
    """Compute cost in USD for a given model and token counts."""
    pricing = PRICING.get(model, {"input": 0.001, "output": 0.003})
    return (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])

def print_config():
    print(f"  Simple   → {MODELS.simple}")
    print(f"  Moderate → {MODELS.moderate}")
    print(f"  Complex  → {MODELS.complex}")
    print(f"  Default  → {MODELS.default}")
