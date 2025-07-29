import os
from pathlib import Path
import toml
from typing import Any, Dict, Optional
import litellm
from litellm import validate_environment

CONFIG_FILENAMES = ["weaver.toml", ".weaverrc"]

# Provider-agnostic model configurations with litellm format translation
LLM_CONFIG = {
    "main_orchestrator": os.getenv("WEAVER_ORCHESTRATOR", "gpt-4o-mini"),
    "available_llms": {
        # OpenAI models
        "gpt-4o-mini": {
            "model": "gpt-4o-mini",  # litellm auto-prefixes openai/
            "max_tokens": 8192,
            "cost_per_1k_tokens": {"prompt": 0.00015, "completion": 0.0006},
            "provider": "openai"
        },
        "gpt-4o": {
            "model": "gpt-4o",
            "max_tokens": 4096,
            "cost_per_1k_tokens": {"prompt": 0.005, "completion": 0.015},
            "provider": "openai"
        },
        
        # Anthropic models
        "claude-3-haiku": {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 4096,
            "cost_per_1k_tokens": {"prompt": 0.00025, "completion": 0.00125},
            "provider": "anthropic"
        },
        "claude-3-sonnet": {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4096,
            "cost_per_1k_tokens": {"prompt": 0.003, "completion": 0.015},
            "provider": "anthropic"
        },
        
        # Google models
        "gemini-1.5-pro": {
            "model": "gemini/gemini-1.5-pro",
            "max_tokens": 8192,
            "cost_per_1k_tokens": {"prompt": 0.0035, "completion": 0.0105},
            "provider": "google"
        },
        "gemini-1.5-flash": {
            "model": "gemini/gemini-1.5-flash",
            "max_tokens": 8192,
            "cost_per_1k_tokens": {"prompt": 0.000075, "completion": 0.0003},
            "provider": "google"
        },
        
        # Other providers can be easily added here...
    },
}

def _load_file_config() -> Dict[str, Any]:
    """Load configuration from weaver.toml or .weaverrc files."""
    for name in CONFIG_FILENAMES:
        path = Path(name)
        if path.exists():
            try:
                return toml.loads(path.read_text())
            except Exception as e:
                print(f"Warning: Failed to parse {name}: {e}")
    return {}

def get_model_config(key: str) -> dict:
    """
    Retrieve the configuration dict for the given llm_config_key.
    Raises KeyError if the key is missing.
    """
    try:
        return LLM_CONFIG["available_llms"][key]
    except KeyError as e:
        available = list(LLM_CONFIG["available_llms"].keys())
        raise KeyError(f"LLM config key '{key}' not found. Available: {available}") from e

def validate_model_credentials(model_key: str) -> bool:
    """
    Validate that credentials are available for the specified model
    using litellm's native validation.
    
    Returns True if valid, False otherwise.
    """
    try:
        config = get_model_config(model_key)
        model_name = config["model"]
        
        # Use litellm's built-in credential validation
        return validate_environment(model_name)
    except Exception:
        return False

def get_missing_credentials() -> Dict[str, list]:
    """
    Check all configured models and return missing credential requirements.
    
    Returns:
        Dict mapping provider names to lists of missing environment variables.
    """
    missing = {}
    
    for model_key, config in LLM_CONFIG["available_llms"].items():
        provider = config.get("provider", "unknown")
        
        if not validate_model_credentials(model_key):
            if provider not in missing:
                missing[provider] = []
            
            # Map providers to their typical credential requirements
            cred_map = {
                "openai": ["OPENAI_API_KEY"],
                "anthropic": ["ANTHROPIC_API_KEY"],
                "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
                "azure": ["AZURE_API_KEY", "AZURE_API_BASE"],
                "cohere": ["COHERE_API_KEY"],
                "replicate": ["REPLICATE_API_TOKEN"],
            }
            
            required_creds = cred_map.get(provider, [f"{provider.upper()}_API_KEY"])
            for cred in required_creds:
                if cred not in missing[provider]:
                    missing[provider].append(cred)
    
    return missing

def setup_litellm_config():
    """
    Configure litellm with any additional settings from config files.
    This allows users to set provider-specific configurations.
    """
    file_config = _load_file_config()
    
    # Set litellm configurations if present
    litellm_config = file_config.get("litellm", {})
    
    # Common litellm settings users might want to configure
    if "drop_params" in litellm_config:
        litellm.drop_params = litellm_config["drop_params"]
    
    if "set_verbose" in litellm_config:
        litellm.set_verbose = litellm_config["set_verbose"]
    
    if "api_base" in litellm_config:
        litellm.api_base = litellm_config["api_base"]
    
    # Allow setting custom API bases for different providers
    api_bases = file_config.get("api_bases", {})
    for provider, base_url in api_bases.items():
        setattr(litellm, f"{provider}_api_base", base_url)

def check_environment() -> Optional[str]:
    """
    Validate that at least one model is properly configured with credentials.
    
    Returns:
        None if valid, error message string if not.
    """
    missing = get_missing_credentials()
    
    if not missing:
        return None
    
    # Check if the main orchestrator is available
    main_model = LLM_CONFIG["main_orchestrator"]
    if not validate_model_credentials(main_model):
        return f"Main orchestrator model '{main_model}' is not properly configured."
    
    # If main orchestrator works, just warn about others
    missing_providers = list(missing.keys())
    if len(missing_providers) == len(LLM_CONFIG["available_llms"]):
        # All models are missing credentials
        error_parts = []
        for provider, creds in missing.items():
            cred_list = " or ".join(creds)
            error_parts.append(f"  {provider}: {cred_list}")
        
        return (
            "No valid model credentials found. Please set one of:\n" +
            "\n".join(error_parts)
        )
    
    return None

# Initialize litellm configuration on import
setup_litellm_config()