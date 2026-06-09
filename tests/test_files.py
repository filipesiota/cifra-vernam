import os
import tempfile
import unittest
from unittest.mock import patch

from main import SALT_SIZE, criptografar_arquivo, decriptografar_arquivo, ler_arquivo


class TestArquivos(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("main.PBKDF2_ITERATIONS", 1)
    def test_criptografar_decriptografar_arquivo(self):
        caminho_original = os.path.join(self.temp_path, "texto.txt")
        conteudo = b"conteudo de teste para round-trip"
        with open(caminho_original, "wb") as f:
            f.write(conteudo)

        senha = "senha-teste"
        caminho_cifrado = criptografar_arquivo(caminho_original, senha)
        self.assertTrue(os.path.isfile(caminho_cifrado))
        self.assertTrue(caminho_cifrado.endswith("_cifrado.txt"))

        caminho_decifrado = decriptografar_arquivo(caminho_cifrado, senha)
        self.assertTrue(os.path.isfile(caminho_decifrado))
        self.assertTrue(caminho_decifrado.endswith("_decifrado.txt"))

        conteudo_recuperado = ler_arquivo(caminho_decifrado)
        self.assertEqual(conteudo_recuperado, conteudo)

    @patch("main.PBKDF2_ITERATIONS", 1)
    def test_arquivo_sample(self):
        caminho_sample = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "samples",
            "arquivo.txt",
        )
        conteudo_original = ler_arquivo(caminho_sample)

        caminho_copia = os.path.join(self.temp_path, "arquivo.txt")
        with open(caminho_copia, "wb") as f:
            f.write(conteudo_original)

        senha = "senha-sample"
        caminho_cifrado = criptografar_arquivo(caminho_copia, senha)
        caminho_decifrado = decriptografar_arquivo(caminho_cifrado, senha)

        conteudo_recuperado = ler_arquivo(caminho_decifrado)
        self.assertEqual(conteudo_recuperado, conteudo_original)

    @patch("main.PBKDF2_ITERATIONS", 1)
    def test_formato_arquivo_cifrado(self):
        caminho_original = os.path.join(self.temp_path, "texto.txt")
        conteudo = b"plaintext para validar formato"
        with open(caminho_original, "wb") as f:
            f.write(conteudo)

        caminho_cifrado = criptografar_arquivo(caminho_original, "senha")
        dados_cifrados = ler_arquivo(caminho_cifrado)

        self.assertGreaterEqual(len(dados_cifrados), SALT_SIZE)
        self.assertNotEqual(dados_cifrados[:SALT_SIZE], conteudo[:SALT_SIZE])


if __name__ == "__main__":
    unittest.main()
