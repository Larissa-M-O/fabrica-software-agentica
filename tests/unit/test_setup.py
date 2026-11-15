"""Testes de inicialização e estrutura do pacote."""
import unittest
import sys
from pathlib import Path

# Adiciona src ao path para os testes se necessário
src_path = str(Path(__file__).resolve().parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import password_validator


class TestSetup(unittest.TestCase):
    def test_package_import(self):
        """Verifica se o pacote password_validator pode ser importado com sucesso."""
        self.assertIsNotNone(password_validator)


if __name__ == "__main__":
    unittest.main()
