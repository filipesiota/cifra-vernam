import unittest
from unittest.mock import patch

from main import SALT_SIZE, _xor_bytes, decrypt, derivar_chave, encrypt


class TestXorBytes(unittest.TestCase):
    def test_xor_bytes_idempotente(self):
        dados = b"plaintext de teste"
        chave = b"keystream123456789"  # mesmo comprimento que dados
        cifrado = _xor_bytes(dados, chave)
        recuperado = _xor_bytes(cifrado, chave)
        self.assertEqual(recuperado, dados)


class TestDerivarChave(unittest.TestCase):
    @patch("main.PBKDF2_ITERATIONS", 1)
    def test_derivar_chave_deterministica(self):
        senha = "minha-senha"
        salt = b"\x00" * SALT_SIZE
        tamanho = 32

        chave1 = derivar_chave(senha, salt, tamanho)
        chave2 = derivar_chave(senha, salt, tamanho)
        self.assertEqual(chave1, chave2)

        salt_diferente = b"\x01" + b"\x00" * (SALT_SIZE - 1)
        chave3 = derivar_chave(senha, salt_diferente, tamanho)
        self.assertNotEqual(chave1, chave3)


class TestEncryptDecrypt(unittest.TestCase):
    @patch("main.PBKDF2_ITERATIONS", 1)
    def test_encrypt_decrypt_roundtrip(self):
        plaintext = b"mensagem secreta"
        senha = "senha-forte"
        ciphertext = encrypt(plaintext, senha)
        self.assertEqual(decrypt(ciphertext, senha), plaintext)

    @patch("main.PBKDF2_ITERATIONS", 1)
    def test_encrypt_prefixo_salt(self):
        plaintext = b"dados"
        ciphertext = encrypt(plaintext, "senha")
        self.assertEqual(len(ciphertext), SALT_SIZE + len(plaintext))

    @patch("main.PBKDF2_ITERATIONS", 1)
    def test_encrypt_salt_aleatorio(self):
        plaintext = b"mesmo conteudo"
        senha = "mesma-senha"
        ciphertext1 = encrypt(plaintext, senha)
        ciphertext2 = encrypt(plaintext, senha)
        self.assertNotEqual(ciphertext1, ciphertext2)

    @patch("main.PBKDF2_ITERATIONS", 1)
    def test_decrypt_senha_incorreta(self):
        plaintext = b"conteudo original"
        senha_correta = "senha-certa"
        senha_errada = "senha-errada"
        ciphertext = encrypt(plaintext, senha_correta)
        resultado = decrypt(ciphertext, senha_errada)
        self.assertNotEqual(resultado, plaintext)

    def test_decrypt_arquivo_curto_demais(self):
        with self.assertRaises(SystemExit) as ctx:
            decrypt(b"curto", "senha")
        self.assertEqual(ctx.exception.code, 1)

    @patch("main.PBKDF2_ITERATIONS", 1)
    def test_roundtrip_vazio(self):
        plaintext = b""
        senha = "senha"
        ciphertext = encrypt(plaintext, senha)
        self.assertEqual(decrypt(ciphertext, senha), plaintext)

    @patch("main.PBKDF2_ITERATIONS", 1)
    def test_roundtrip_utf8(self):
        plaintext = "Olá! @#$".encode("utf-8")
        senha = "senha-utf8"
        ciphertext = encrypt(plaintext, senha)
        self.assertEqual(decrypt(ciphertext, senha), plaintext)


if __name__ == "__main__":
    unittest.main()
