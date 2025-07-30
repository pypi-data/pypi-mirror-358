from .core import A007ProXFinal
from .utils import calculate_entropy

# Singleton hasher instance
_hasher_instance = None


def configure(key: str, iterations: int = 200_000, secure_delay: bool = False):
    """
    Configure the hashing engine with key, iterations, and secure mode
    """
    global _hasher_instance
    _hasher_instance = A007ProXFinal(key=key, iterations=iterations, secure_delay=secure_delay)


def hash_text(text: str) -> str:
    """
    Generate a secure deterministic hash for given text
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    return _hasher_instance.hash(text)


def verify(text: str, hashed: str) -> bool:
    """
    Verify whether the provided text matches the given hash
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    try:
        new_hash = _hasher_instance.hash(text)
        return new_hash == hashed
    except Exception:
        return False


def set_key(new_key: str):
    """
    Change the key dynamically and regenerate derived values
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    _hasher_instance.key = new_key
    _hasher_instance.derived_key = _hasher_instance._derive_key()
    _hasher_instance.base_table = _hasher_instance._build_base_table()


def set_iterations(new_iterations: int):
    """
    Update iteration count (strength of hash derivation)
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    _hasher_instance.iterations = new_iterations
    _hasher_instance.derived_key = _hasher_instance._derive_key()


def get_entropy(text: str) -> float:
    """
    Calculate entropy of a given hash string
    """
    return calculate_entropy(text)


def export_config() -> dict:
    """
    Export current configuration as dictionary (safe inspection)
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")

    key_length = "CLEARED"
    if hasattr(_hasher_instance, "key") and _hasher_instance.key is not None:
        key_length = len(_hasher_instance.key)

    return {
        "key_length": key_length,
        "iterations": _hasher_instance.iterations,
        "secure_delay": _hasher_instance.secure_delay,
        "base_table_length": len(_hasher_instance.base_table)
    }


def secure_mode(enable: bool = True):
    """
    Enable or disable secure delay (adds randomness to processing time)
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    _hasher_instance.secure_delay = enable
