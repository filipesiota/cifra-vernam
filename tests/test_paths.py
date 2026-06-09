import os
import unittest

from main import caminho_arquivo_cifrado, caminho_arquivo_decifrado


class TestCaminhosArquivo(unittest.TestCase):
    def test_caminho_cifrado(self):
        self.assertEqual(
            caminho_arquivo_cifrado("texto.txt"),
            "texto_cifrado.txt",
        )

    def test_caminho_cifrado_com_diretorio(self):
        self.assertEqual(
            caminho_arquivo_cifrado("dir/texto.txt"),
            os.path.join("dir", "texto_cifrado.txt"),
        )

    def test_caminho_decifrado(self):
        self.assertEqual(
            caminho_arquivo_decifrado("texto_cifrado.txt"),
            "texto_decifrado.txt",
        )

    def test_caminho_decifrado_sem_sufixo(self):
        self.assertEqual(
            caminho_arquivo_decifrado("texto.txt"),
            "texto_decifrado.txt",
        )


if __name__ == "__main__":
    unittest.main()
