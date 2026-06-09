import io
import os
import tempfile
import unittest
from unittest.mock import patch

from main import MENSAGEM_USO, validar_argumentos


class TestValidarArgumentos(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.caminho_arquivo = os.path.join(self.temp_dir.name, "texto.txt")
        with open(self.caminho_arquivo, "wb") as f:
            f.write(b"conteudo")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_argumentos_validos(self):
        argv = ["main.py", self.caminho_arquivo, "minha-senha", "criptografar"]
        resultado = validar_argumentos(argv)
        self.assertEqual(resultado, (self.caminho_arquivo, "minha-senha", "criptografar"))

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_argumentos_insuficientes(self, mock_stderr):
        with self.assertRaises(SystemExit) as ctx:
            validar_argumentos(["main.py"])
        self.assertEqual(ctx.exception.code, 1)
        stderr = mock_stderr.getvalue()
        self.assertIn("Uso: python main.py", stderr)
        self.assertIn(MENSAGEM_USO.strip(), stderr)

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_arquivo_inexistente(self, mock_stderr):
        caminho_inexistente = os.path.join(self.temp_dir.name, "nao_existe.txt")
        argv = ["main.py", caminho_inexistente, "senha", "criptografar"]
        with self.assertRaises(SystemExit) as ctx:
            validar_argumentos(argv)
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("arquivo não encontrado", mock_stderr.getvalue())
        self.assertIn(caminho_inexistente, mock_stderr.getvalue())

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_operacao_invalida(self, mock_stderr):
        argv = ["main.py", self.caminho_arquivo, "senha", "invalida"]
        with self.assertRaises(SystemExit) as ctx:
            validar_argumentos(argv)
        self.assertEqual(ctx.exception.code, 1)
        stderr = mock_stderr.getvalue()
        self.assertIn("operação inválida", stderr)
        self.assertIn("invalida", stderr)


if __name__ == "__main__":
    unittest.main()
