from .core import A007ProXFinal
from .utils import calculate_entropy

# متغیر singleton برای استفاده راحت در پروژه
_hasher_instance = None

def configure(key: str, iterations: int = 200_000, secure_delay: bool = False):
    """
    پیکربندی اولیه (کلید، تعداد تکرار و حالت امن)
    """
    global _hasher_instance
    _hasher_instance = A007ProXFinal(key=key, iterations=iterations, secure_delay=secure_delay)

def hash_text(text: str) -> str:
    """
    هش ساده با پیکربندی فعلی
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    return _hasher_instance.hash(text)

def verify(text: str, hashed: str) -> bool:
    """
    مقایسه هش با متن اصلی
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
    تغییر کلید در پیکربندی فعلی
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    _hasher_instance.key = new_key
    _hasher_instance.derived_key = _hasher_instance._derive_key()
    _hasher_instance.base_table = _hasher_instance._build_base_table()

def set_iterations(new_iterations: int):
    """
    تنظیم قدرت تکرار هش (Iterations)
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    _hasher_instance.iterations = new_iterations
    _hasher_instance.derived_key = _hasher_instance._derive_key()

def get_entropy(text: str) -> float:
    """
    بررسی کیفیت هش (Entropy) از utils
    """
    return calculate_entropy(text)

def export_config() -> dict:
    """
    خروجی گرفتن از تنظیمات فعلی
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    return {
        "key_length": len(_hasher_instance.key),
        "iterations": _hasher_instance.iterations,
        "secure_delay": _hasher_instance.secure_delay,
        "base_table_length": len(_hasher_instance.base_table)
    }

def secure_mode(enable: bool = True):
    """
    فعال یا غیرفعال کردن حالت امنیتی (secure_delay)
    """
    if _hasher_instance is None:
        raise RuntimeError("Hasher is not configured. Call configure() first.")
    _hasher_instance.secure_delay = enable
