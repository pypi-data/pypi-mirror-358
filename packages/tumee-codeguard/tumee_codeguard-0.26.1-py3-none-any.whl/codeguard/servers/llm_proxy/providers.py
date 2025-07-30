"""
Provider definitions and utilities for LLM proxy server.
"""

from enum import Enum
from typing import Dict, List


class Provider(str, Enum):
    """Supported LLM providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    MISTRAL = "mistral"
    COHERE = "cohere"
    REPLICATE = "replicate"
    HUGGINGFACE = "huggingface"
    TOGETHER = "together"
    GROQ = "groq"
    UNKNOWN = "unknown"


# Default provider path mappings
DEFAULT_PROVIDER_PATHS: Dict[str, List[str]] = {
    Provider.OPENAI: ["/v1/chat/completions", "/chat/completions", "/v1/completions"],
    Provider.ANTHROPIC: ["/v1/messages", "/messages", "/v1/complete"],
    Provider.GOOGLE: ["/v1/models/*/generateContent", "/v1beta/models/*/generateContent"],
    Provider.AZURE: ["/openai/deployments/*/chat/completions"],
    Provider.MISTRAL: ["/v1/chat/completions"],
    Provider.GROQ: ["/openai/v1/chat/completions"],
    Provider.COHERE: ["/v1/chat"],
    Provider.TOGETHER: ["/v1/chat/completions"],
    Provider.HUGGINGFACE: ["/v1/chat/completions"],
}


def detect_provider_from_path(path: str, provider_paths: Dict[str, List[str]] = None) -> Provider:
    """Detect provider from request path"""
    if provider_paths is None:
        provider_paths = DEFAULT_PROVIDER_PATHS

    path = path.lower()

    for provider, paths in provider_paths.items():
        for provider_path in paths:
            # Handle wildcard paths
            if "*" in provider_path:
                pattern = provider_path.replace("*", ".*")
                import re

                if re.match(pattern, path):
                    return provider
            elif path.startswith(provider_path):
                return provider

    return Provider.UNKNOWN


def detect_provider_from_model(model: str) -> Provider:
    """Detect provider from model name"""
    model_lower = model.lower()

    if model_lower.startswith(("gpt-", "text-davinci", "text-embedding", "dall-e")):
        return Provider.OPENAI
    elif model_lower.startswith(("claude-", "anthropic/")):
        return Provider.ANTHROPIC
    elif model_lower.startswith(("gemini-", "palm-", "models/gemini")):
        return Provider.GOOGLE
    elif model_lower.startswith(("mistral", "mixtral", "codestral")):
        return Provider.MISTRAL
    elif model_lower.startswith(("command-", "cohere/")):
        return Provider.COHERE
    elif "together" in model_lower:
        return Provider.TOGETHER
    elif model_lower.startswith(("meta-llama", "llama-")):
        # Could be multiple providers, check for specific patterns
        if "groq" in model_lower:
            return Provider.GROQ
        elif "together" in model_lower:
            return Provider.TOGETHER
        else:
            return Provider.HUGGINGFACE

    return Provider.UNKNOWN


def detect_provider(
    path: str, model: str, headers: Dict[str, str], provider_paths: Dict[str, List[str]] = None
) -> Provider:
    """Detect provider from path first, then model name as fallback"""
    # First try path-based detection
    provider = detect_provider_from_path(path, provider_paths)
    if provider != Provider.UNKNOWN:
        return provider

    # Check for Azure in path or headers
    if "azure" in model.lower() or "deployment" in path or "azure" in headers.get("host", ""):
        return Provider.AZURE

    # Check for Groq in headers
    if "groq" in headers.get("host", ""):
        return Provider.GROQ

    # Fallback to model-based detection
    return detect_provider_from_model(model)
