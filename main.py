import hashlib
import os

# Parâmetros da derivação de chave PBKDF2
PBKDF2_HASH = "sha256"
PBKDF2_ITERATIONS = 200_000
SALT_SIZE = 16


def _xor_bytes(dados: bytes, chave: bytes) -> bytes:
    """
    Aplica XOR bit a bit entre cada byte dos dados e o byte correspondente da chave.

    A Cifra de Vernam combina plaintext e keystream com XOR. Como XOR é sua própria
    inversa, a mesma operação serve para cifrar e decifrar.
    """
    return bytes(a ^ b for a, b in zip(dados, chave))


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


def encrypt(plaintext: bytes, senha: str) -> bytes:
    """
    Cifra o plaintext com a Cifra de Vernam.

    Gera um salt aleatório, deriva um keystream do mesmo tamanho da mensagem via
    PBKDF2 e aplica XOR byte a byte. Retorna salt + ciphertext para que a
    decriptação possa re-derivar a mesma chave.
    """
    # Salt aleatório garante keystream único por arquivo, mesmo com a mesma senha
    salt = os.urandom(SALT_SIZE)

    # Keystream com o mesmo comprimento do plaintext (requisito da Cifra de Vernam)
    chave = derivar_chave(senha, salt, len(plaintext))

    # XOR: cada byte do plaintext com o byte correspondente do keystream
    ciphertext = _xor_bytes(plaintext, chave)

    # Formato de saída: salt (16 bytes) seguido dos dados cifrados
    return salt + ciphertext


def decrypt(ciphertext: bytes, senha: str) -> bytes:
    """
    Decifra dados produzidos por encrypt().

    Extrai o salt dos primeiros 16 bytes, re-deriva o keystream com a mesma senha
    e aplica XOR sobre o restante do arquivo (operação idêntica à cifragem).
    """
    if len(ciphertext) < SALT_SIZE:
        raise ValueError(
            f"Arquivo cifrado inválido: esperado pelo menos {SALT_SIZE} bytes (salt)."
        )

    # Salt armazenado na cifragem: necessário para re-derivar o keystream
    salt = ciphertext[:SALT_SIZE]
    dados_cifrados = ciphertext[SALT_SIZE:]

    # Mesma derivação PBKDF2 (senha + salt) produz o mesmo keystream
    chave = derivar_chave(senha, salt, len(dados_cifrados))

    # XOR novamente recupera o plaintext original
    return _xor_bytes(dados_cifrados, chave)
