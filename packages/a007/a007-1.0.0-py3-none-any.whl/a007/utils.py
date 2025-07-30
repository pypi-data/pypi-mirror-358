import math
from collections import Counter

def calculate_entropy(text: str) -> float:
    """
    محاسبه آنتروپی یک متن بر اساس توزیع کاراکترها
    مقدار بیشتر نشانه تصادفی‌بودن بالاتر است
    """
    if not text:
        return 0.0

    freq = Counter(text)
    length = len(text)
    entropy = -sum((count / length) * math.log2(count / length) for count in freq.values())
    return round(entropy, 4)


def format_entropy_report(text: str) -> str:
    entropy = calculate_entropy(text)
    if entropy < 3.5:
        strength = "❌ ضعیف (Weak)"
    elif entropy < 4.5:
        strength = "⚠️ متوسط (Moderate)"
    elif entropy < 5.5:
        strength = "✅ قوی (Strong)"
    else:
        strength = "💎 بسیار قوی (Very Strong)"

    return f"Entropy: {entropy} → {strength}"
