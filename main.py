import hashlib

# Parâmetros da derivação de chave PBKDF2
PBKDF2_HASH = "sha256"
PBKDF2_ITERATIONS = 200_000
SALT_SIZE = 16


def derivar_chave(senha: str, salt: bytes, tamanho: int) -> bytes:
    """
    Deriva um keystream do tamanho necessário a partir da senha e do salt.

    Usa PBKDF2-HMAC-SHA256 com 200.000 iterações. O salt aleatório (gerado
    na cifragem e armazenado nos primeiros 16 bytes do arquivo cifrado) torna
    cada keystream único, resistindo a ataques de rainbow tables.
    """
    senha_bytes = senha.encode("utf-8")
    return hashlib.pbkdf2_hmac(
        PBKDF2_HASH,
        senha_bytes,
        salt,
        PBKDF2_ITERATIONS,
        dklen=tamanho,
    )
