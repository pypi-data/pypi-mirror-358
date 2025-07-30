# presets.py

# تنظیمات پیش‌فرض الگوریتم A-007 Pro X Final

def default_config():
    return {
        "iterations": 200_000,
        "secure_delay": False,
        "entropy_thresholds": {
            "weak": 3.5,
            "moderate": 4.5,
            "strong": 5.5
        },
        "hash_length": 86,
        "base_chars": (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789"
            "!@#$%^&*()-_=+[]{}<>?/|~"
        )[:86],
        "salt_suffix": "::A007_SALT"
    }


def get_threshold_label(entropy: float) -> str:
    if entropy < 3.5:
        return "❌ Weak"
    elif entropy < 4.5:
        return "⚠️ Moderate"
    elif entropy < 5.5:
        return "✅ Strong"
    else:
        return "💎 Very Strong"
