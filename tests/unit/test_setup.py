"""Testes de inicialização, estrutura e exportações públicas do pacote."""
import sys
from pathlib import Path
import unittest

# Adiciona src ao path para os testes se necessário
src_path = str(Path(__file__).resolve().parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import password_validator
from password_validator import (
    CodigoCriterio,
    NivelForca,
    ResultadoCriterio,
    ResultadoValidacao,
    eh_senha_valida,
    validar_senha,
)


class TestSetup(unittest.TestCase):
    def test_package_import(self):
        """Verifica se o pacote password_validator pode ser importado com sucesso."""
        self.assertIsNotNone(password_validator)

    def test_public_api_exports(self):
        """Verifica se todos os itens públicos especificados em __all__ estão disponíveis."""
        exportacoes_esperadas = [
            "validar_senha",
            "eh_senha_valida",
            "ResultadoValidacao",
            "ResultadoCriterio",
            "NivelForca",
            "CodigoCriterio",
        ]
        self.assertEqual(password_validator.__all__, exportacoes_esperadas)
        for item in exportacoes_esperadas:
            self.assertTrue(hasattr(password_validator, item))


if __name__ == "__main__":
    unittest.main()
