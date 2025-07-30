from .core import A007ProXFinal
from .utils import calculate_entropy

# Singleton instance for easy global use
_hasher_instance = None

def configure(key: str, iterations: int = 200_000, secure_delay: bool = False):
    global _hasher_instance
    _hasher_instance = A007ProXFinal(key=key, iterations=iterations, secure_delay=secure_delay)

def hash_text(text: str) -> str:
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    return _hasher_instance.hash(text)

def verify(text: str, hashed: str) -> bool:
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    try:
        return _hasher_instance.hash(text) == hashed
    except Exception:
        return False

def set_key(new_key: str):
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    _hasher_instance.key = new_key
    _hasher_instance.derived_key = _hasher_instance._derive_key()
    _hasher_instance.base_table = _hasher_instance._build_base_table()

def set_iterations(new_iterations: int):
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    _hasher_instance.iterations = new_iterations
    _hasher_instance.derived_key = _hasher_instance._derive_key()

def get_entropy(text: str) -> float:
    return calculate_entropy(text)

def export_config() -> dict:
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    # نمایش طول کلید واقعی اگر کلید وجود داشته باشه
    key_length = len(_hasher_instance.key) if hasattr(_hasher_instance, 'key') else 'CLEARED'
    return {
        "key_length": key_length,
        "iterations": _hasher_instance.iterations,
        "secure_delay": _hasher_instance.secure_delay,
        "base_table_length": len(_hasher_instance.base_table)
    }

def secure_mode(enable: bool = True):
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    _hasher_instance.secure_delay = enable
