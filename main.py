import hashlib
import os
import sys

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

    if not plaintext:
        return salt

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
        print(
            f"Erro: arquivo cifrado inválido: esperado pelo menos {SALT_SIZE} bytes (salt).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Salt armazenado na cifragem: necessário para re-derivar o keystream
    salt = ciphertext[:SALT_SIZE]
    dados_cifrados = ciphertext[SALT_SIZE:]

    if not dados_cifrados:
        return b""

    # Mesma derivação PBKDF2 (senha + salt) produz o mesmo keystream
    chave = derivar_chave(senha, salt, len(dados_cifrados))

    # XOR novamente recupera o plaintext original
    return _xor_bytes(dados_cifrados, chave)


def ler_arquivo(caminho: str) -> bytes:
    """Lê o conteúdo completo de um arquivo em modo binário."""
    with open(caminho, "rb") as arquivo:
        return arquivo.read()


def gravar_arquivo(caminho: str, dados: bytes) -> None:
    """Grava bytes em um arquivo em modo binário."""
    with open(caminho, "wb") as arquivo:
        arquivo.write(dados)


def caminho_arquivo_cifrado(caminho_entrada: str) -> str:
    """
    Gera o caminho de saída para cifragem: remove a extensão .txt e adiciona _cifrado.txt.

    Exemplo: texto.txt -> texto_cifrado.txt
    """
    diretorio, nome = os.path.split(caminho_entrada)
    if nome.endswith(".txt"):
        nome_base = nome[:-4]
    else:
        nome_base = nome
    return os.path.join(diretorio, f"{nome_base}_cifrado.txt")


def caminho_arquivo_decifrado(caminho_entrada: str) -> str:
    """
    Gera o caminho de saída para decifragem: remove o sufixo _cifrado.txt e adiciona _decifrado.txt.

    Exemplo: texto_cifrado.txt -> texto_decifrado.txt
    """
    diretorio, nome = os.path.split(caminho_entrada)
    if nome.endswith("_cifrado.txt"):
        nome_base = nome[: -len("_cifrado.txt")]
    elif nome.endswith(".txt"):
        nome_base = nome[:-4]
    else:
        nome_base = nome
    return os.path.join(diretorio, f"{nome_base}_decifrado.txt")


def criptografar_arquivo(caminho_entrada: str, senha: str) -> str:
    """
    Lê o arquivo de entrada, cifra com a Cifra de Vernam e grava salt + ciphertext.

    Retorna o caminho do arquivo _cifrado.txt gerado.
    """
    plaintext = ler_arquivo(caminho_entrada)
    dados_cifrados = encrypt(plaintext, senha)
    caminho_saida = caminho_arquivo_cifrado(caminho_entrada)
    gravar_arquivo(caminho_saida, dados_cifrados)
    return caminho_saida


def decriptografar_arquivo(caminho_entrada: str, senha: str) -> str:
    """
    Lê o arquivo cifrado (salt + ciphertext), decifra e grava o plaintext.

    Retorna o caminho do arquivo _decifrado.txt gerado.
    """
    dados_cifrados = ler_arquivo(caminho_entrada)
    plaintext = decrypt(dados_cifrados, senha)
    caminho_saida = caminho_arquivo_decifrado(caminho_entrada)
    gravar_arquivo(caminho_saida, plaintext)
    return caminho_saida


OPERACOES_VALIDAS = frozenset({"criptografar", "decriptografar"})

MENSAGEM_USO = """\
Uso: python main.py <arquivo> <senha> <operacao>

Operações válidas: criptografar, decriptografar
"""


def validar_argumentos(argv: list[str]) -> tuple[str, str, str]:
    """
    Valida os argumentos da linha de comando e retorna (arquivo, senha, operação).

    Encerra o programa com mensagem de erro quando:
    - o número de argumentos é incorreto;
    - o arquivo de entrada não existe;
    - a operação não é 'criptografar' nem 'decriptografar'.
    """
    if len(argv) != 4:
        print(MENSAGEM_USO, file=sys.stderr)
        sys.exit(1)

    _, caminho_arquivo, senha, operacao = argv

    if not os.path.isfile(caminho_arquivo):
        print(f"Erro: arquivo não encontrado: {caminho_arquivo}", file=sys.stderr)
        sys.exit(1)

    if operacao not in OPERACOES_VALIDAS:
        print(
            f"Erro: operação inválida '{operacao}'. "
            "Use 'criptografar' ou 'decriptografar'.",
            file=sys.stderr,
        )
        sys.exit(1)

    return caminho_arquivo, senha, operacao


def main() -> None:
    """Ponto de entrada: valida argumentos e executa cifragem ou decifragem."""
    caminho_arquivo, senha, operacao = validar_argumentos(sys.argv)

    if operacao == "criptografar":
        caminho_saida = criptografar_arquivo(caminho_arquivo, senha)
    else:
        caminho_saida = decriptografar_arquivo(caminho_arquivo, senha)

    print(f"Arquivo gravado em: {caminho_saida}")


if __name__ == "__main__":
    main()
