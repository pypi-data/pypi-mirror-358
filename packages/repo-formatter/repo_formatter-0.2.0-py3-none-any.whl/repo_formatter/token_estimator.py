import tiktoken

def estimate_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Estimates tokens using tiktoken library.
    Falls back to basic estimation if tiktoken fails.
    """
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(text))
        return num_tokens
    except Exception as e:
        print(f"Warning: tiktoken estimation failed ({e}). Falling back to basic estimation.")
        return _estimate_tokens_fallback(text)

def _estimate_tokens_fallback(text: str) -> int:
    """
    Provides a very rough estimate of token count.
    A common rule of thumb is ~4 characters per token.
    """
    # Simple character-based estimate
    estimated_tokens = len(text) / 4
    return int(estimated_tokens)