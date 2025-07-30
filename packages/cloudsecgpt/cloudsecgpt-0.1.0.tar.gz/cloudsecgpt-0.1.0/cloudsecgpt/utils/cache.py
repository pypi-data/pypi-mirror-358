import hashlib
import sys
from pathlib import Path

from cloudsecgpt.utils.console import console

# Directory where all cache files will live
CACHE_DIR = Path.home() / ".cgpt_cache"
CACHE_DIR.mkdir(exist_ok=True)


def make_cache_path(
    *,
    key: str = "",
    namespace: str = "",
    provider: str = "",
    model: str = "",
    prompt: str = "",
    digest_size: int = 16,
) -> Path:
    """
    Build a unique cache path by hashing:
      - namespace: e.g. SHA1 of the input file contents
      - provider:  "openai" or "ollama" or "bedrock" or "mcp"
      - model:     model name
      - prompt:    serialized prompt/messages
    Uses BLAKE2b for speed and to avoid security alerts.
    """
    try:
        if key:
            key = f"{key}".encode()
        else:
            key = f"{namespace}:{provider}:{model}:{prompt}".encode()
        hash_hex = hashlib.blake2b(key, digest_size=digest_size).hexdigest()
        return CACHE_DIR / f"{hash_hex}.cache"
    except Exception as e:
        console.log(f"[red]Cache error: {e}[/red]")
        sys.exit(1)
