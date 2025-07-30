import hashlib
import hmac
import secrets
import string
import base64
import time
import gc
from .presets import default_config

class A007ProXFinal:
    def __init__(self, key: str,
                 iterations: int = None,
                 secure_delay: bool = None):
        config = default_config()
        self.key = key
        self.iterations = iterations if iterations is not None else config["iterations"]
        self.secure_delay = secure_delay if secure_delay is not None else config["secure_delay"]
        self.salt_suffix = config["salt_suffix"]
        self.base_chars = config["base_chars"]
        self.hash_length = config["hash_length"]

        self.derived_key = self._derive_key()
        self.base_table = self._build_base_table()

    def _derive_key(self) -> bytes:
        salt = hashlib.sha3_512((self.key + self.salt_suffix).encode()).digest()
        return hashlib.pbkdf2_hmac('sha512', self.key.encode(), salt, self.iterations)

    def _build_base_table(self) -> list:
        table = list(self.base_chars)
        # Use a deterministic shuffle based on derived_key so it's consistent
        # This is key to getting same hash for same key+text across runs
        random_gen = secrets.SystemRandom()
        # But secrets.SystemRandom().shuffle is non-deterministic, so we need a deterministic shuffle:
        # Instead let's do a simple deterministic shuffle using derived_key as seed
        seed_int = int.from_bytes(self.derived_key, 'big')
        # Fisher-Yates shuffle with deterministic seed
        table_copy = table[:]
        for i in reversed(range(1, len(table_copy))):
            j = seed_int % (i + 1)
            table_copy[i], table_copy[j] = table_copy[j], table_copy[i]
            seed_int = seed_int // (i + 1)
        return table_copy

    def _multi_layer_hash(self, text: str) -> bytes:
        h1 = hashlib.sha512(text.encode()).digest()
        h2 = hashlib.sha3_256(h1).digest()
        h3 = hashlib.blake2b(h2, digest_size=64).digest()
        return h3

    def _matrix_jump(self, ch: str, idx: int, seed: bytes) -> str:
        jump_input = (ch + str(idx)).encode()
        h = hmac.new(seed, jump_input, hashlib.sha256).digest()
        jump = sum(h) % 100
        i = idx % len(self.base_table)
        while jump > 0:
            if i + 1 >= len(self.base_table):
                i -= 1
            else:
                i += 1
            jump -= 1
        return self.base_table[i]

    def _transform(self, hash_bytes: bytes) -> str:
        result = []
        for i in range(43):
            c1 = chr(hash_bytes[i % len(hash_bytes)])
            c2 = chr(hash_bytes[-(i + 1) % len(hash_bytes)])
            result.append(self._matrix_jump(c1, i, self.derived_key))
            result.append(self._matrix_jump(c2, i, self.derived_key[::-1]))
        return ''.join(result)

    def _base85_encode(self, text: str) -> str:
        encoded = base64.a85encode(text.encode()).decode()
        return encoded[:self.hash_length].ljust(self.hash_length, '~')

    def hash(self, text: str) -> str:
        if self.secure_delay:
            time.sleep(secrets.randbelow(200) / 1000)  # secure delay

        combined = f"{self.key}::{text}"
        hashed = self._multi_layer_hash(combined)
        transformed = self._transform(hashed)
        encoded = self._base85_encode(transformed)

        self._clear_sensitive_data()
        return encoded

    def _clear_sensitive_data(self):
        try:
            del self.key
        except AttributeError:
            pass
        gc.collect()
