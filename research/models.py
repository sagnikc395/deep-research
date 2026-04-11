"""Agno model factory for HuggingFace Inference API with provider routing.

HuggingFace routes requests through third-party inference providers
(novita, together, auto) via its router. Each provider maps to a
distinct base URL that accepts the OpenAI-compatible chat completions
API with the HF token as the API key.
"""
import os
from agno.models.openai import OpenAILike

_PROVIDER_URLS: dict[str, str] = {
    "auto":     "https://api-inference.huggingface.co/v1",
    "novita":   "https://router.huggingface.co/novita/v1",
    "together": "https://router.huggingface.co/together/v1",
}

_BILL_HEADERS = {"X-Bill-To": "huggingface"}


def hf_model(model_id: str, provider: str = "auto") -> OpenAILike:
    """Return an Agno model that calls the HuggingFace Inference API.

    Args:
        model_id: HuggingFace model identifier (e.g. "MiniMaxAI/MiniMax-M1-80k").
        provider: Inference provider to route through ("auto", "novita", "together").
    """
    base_url = _PROVIDER_URLS.get(provider, _PROVIDER_URLS["auto"])
    return OpenAILike(
        id=model_id,
        api_key=os.environ["HF_TOKEN"],
        base_url=base_url,
        default_headers=_BILL_HEADERS,
    )
