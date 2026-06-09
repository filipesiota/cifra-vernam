# Cifra de Vernam

Implementação em Python da Cifra de Vernam (cifra de fluxo baseada em XOR), com derivação de chave via PBKDF2.

## Requisitos

- Python 3.x

## Uso

```bash
python main.py arquivo.txt minhaSenha criptografar
python main.py arquivo_cifrado.txt minhaSenha decriptografar
```

## Formato do arquivo cifrado

- Bytes 0–15: salt aleatório (16 bytes)
- Bytes 16+: dados cifrados (XOR do plaintext com o keystream PBKDF2)

## Convenção de nomenclatura

| Operação       | Entrada              | Saída                  |
|----------------|----------------------|------------------------|
| criptografar   | `texto.txt`          | `texto_cifrado.txt`    |
| decriptografar | `texto_cifrado.txt`  | `texto_decifrado.txt`  |
