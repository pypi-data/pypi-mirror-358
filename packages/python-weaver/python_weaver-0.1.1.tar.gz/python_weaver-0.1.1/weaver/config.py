import os
from pathlib import Path
import toml
from typing import Any, Dict

CONFIG_FILENAMES = ["weaver.toml", ".weaverrc"]
LLM_CONFIG = {
    "main_orchestrator": os.getenv("WEAVER_ORCHESTRATOR", "gpt-4o-mini"),
    "available_llms": {
        "gpt-4o-mini": {
            "model": "openai/gpt-4o-mini",
            "max_tokens": 8192,
            "cost_per_1k_tokens": {"prompt": 0.0015, "completion": 0.0020},
            
        },
        "gemini-1.5-pro": {
            "model": "gemini/gemini-1.5-pro",
            "max_tokens": 8192,
            "cost_per_1k_tokens": {"prompt": 0.0020, "completion": 0.0025},
        },
        # Users can add more models here…
    },
}
def _load_file_config() -> Dict[str, Any]:
    for name in CONFIG_FILENAMES:
        path = Path(name)
        if path.exists():
            data = toml.loads(path.read_text())
            creds = data.get("credentials", {})
            if "openai_api_key" in creds:
                return creds
    return {}

def get_openai_api_key(cli_key: str = None) -> str:
    """
    Resolution order:
      1) CLI-supplied key
      2) OPENAI_API_KEY env var
      3) weaver.toml / .weaverrc credentials.openai_api_key
    """
    if cli_key:
        return cli_key

    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key

    file_cfg = _load_file_config()
    if file_cfg.get("openai_api_key"):
        return file_cfg["openai_api_key"]

    raise EnvironmentError(
        "Missing OpenAI API key: please supply via --api-key, "
        "set OPENAI_API_KEY, or add it to weaver.toml under [credentials]."
    )

def get_model_config(key: str) -> dict:
    """
    Retrieve the configuration dict for the given llm_config_key.
    Raises KeyError if the key is missing.
    """
    try:
        return LLM_CONFIG["available_llms"][key]
    except KeyError as e:
        raise KeyError(f"LLM config key '{key}' not found in LLM_CONFIG.") from e