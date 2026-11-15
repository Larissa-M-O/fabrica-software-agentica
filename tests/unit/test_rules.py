"""Testes unitários das regras estruturais de validação de senha (US1, FR-001 a FR-005)."""
import sys
from pathlib import Path
import unittest

# Adiciona src ao sys.path
src_path = str(Path(__file__).resolve().parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from password_validator.models import CodigoCriterio
from password_validator.rules import (
    validar_especiais,
    validar_maiusculas,
    validar_minusculas,
    validar_numeros,
    validar_tamanho_minimo,
)


class TestRegrasEstruturais(unittest.TestCase):
    """Testes para as funções avaliadoras de regras estruturais de complexidade."""

    def test_cenario_1_1_senha_atende_todos_criterios_estruturais(self):
        """Cenário 1.1: Senha com 10 caracteres contendo maiúsculas, minúsculas, números e especiais."""
        senha = "Abcd1234!@"
        res_tamanho = validar_tamanho_minimo(senha)
        res_maiusculas = validar_maiusculas(senha)
        res_minusculas = validar_minusculas(senha)
        res_numeros = validar_numeros(senha)
        res_especiais = validar_especiais(senha)

        self.assertTrue(res_tamanho.atendido)
        self.assertEqual(res_tamanho.codigo, CodigoCriterio.TAMANHO_MINIMO)
        self.assertEqual(res_tamanho.mensagem, "")

        self.assertTrue(res_maiusculas.atendido)
        self.assertEqual(res_maiusculas.codigo, CodigoCriterio.MAIUSCULAS)
        self.assertEqual(res_maiusculas.mensagem, "")

        self.assertTrue(res_minusculas.atendido)
        self.assertEqual(res_minusculas.codigo, CodigoCriterio.MINUSCULAS)
        self.assertEqual(res_minusculas.mensagem, "")

        self.assertTrue(res_numeros.atendido)
        self.assertEqual(res_numeros.codigo, CodigoCriterio.NUMEROS)
        self.assertEqual(res_numeros.mensagem, "")

        self.assertTrue(res_especiais.atendido)
        self.assertEqual(res_especiais.codigo, CodigoCriterio.ESPECIAIS)
        self.assertEqual(res_especiais.mensagem, "")

    def test_cenario_1_2_tamanho_minimo(self):
        """Cenário 1.2: Senha com comprimento inferior ao mínimo (FR-001)."""
        # Senha com 5 caracteres
        res_curta = validar_tamanho_minimo("Ab1!x")
        self.assertFalse(res_curta.atendido)
        self.assertEqual(res_curta.codigo, CodigoCriterio.TAMANHO_MINIMO)
        self.assertIn("mínimo 8 caracteres", res_curta.mensagem)

        # Senha com exatamente 7 caracteres (limite inferior não atendido)
        res_limite_7 = validar_tamanho_minimo("Ab1!xyz")
        self.assertFalse(res_limite_7.atendido)

        # Senha com exatamente 8 caracteres (fronteira atendida)
        res_limite_8 = validar_tamanho_minimo("Ab1!xyzw")
        self.assertTrue(res_limite_8.atendido)
        self.assertEqual(res_limite_8.mensagem, "")

    def test_cenario_1_3_maiusculas(self):
        """Cenário 1.3: Senha sem letras maiúsculas (FR-003)."""
        # Senha sem maiúsculas
        res_sem_maiuscula = validar_maiusculas("senha123!")
        self.assertFalse(res_sem_maiuscula.atendido)
        self.assertEqual(res_sem_maiuscula.codigo, CodigoCriterio.MAIUSCULAS)
        self.assertIn("ao menos uma letra maiúscula", res_sem_maiuscula.mensagem)

        # Senha com maiúscula
        res_com_maiuscula = validar_maiusculas("Senha123!")
        self.assertTrue(res_com_maiuscula.atendido)
        self.assertEqual(res_com_maiuscula.mensagem, "")

        # Senha com maiúscula Unicode
        res_unicode = validar_maiusculas("coração!123Á")
        self.assertTrue(res_unicode.atendido)

    def test_cenario_1_4_minusculas(self):
        """Cenário 1.4: Senha sem letras minúsculas (FR-002)."""
        # Senha sem minúsculas
        res_sem_minuscula = validar_minusculas("SENHA123!")
        self.assertFalse(res_sem_minuscula.atendido)
        self.assertEqual(res_sem_minuscula.codigo, CodigoCriterio.MINUSCULAS)
        self.assertIn("ao menos uma letra minúscula", res_sem_minuscula.mensagem)

        # Senha com minúscula
        res_com_minuscula = validar_minusculas("Senha123!")
        self.assertTrue(res_com_minuscula.atendido)
        self.assertEqual(res_com_minuscula.mensagem, "")

        # Senha com minúscula Unicode
        res_unicode = validar_minusculas("CORAÇÃO!123ã")
        self.assertTrue(res_unicode.atendido)

    def test_cenario_1_5_numeros(self):
        """Cenário 1.5: Senha sem dígitos numéricos (FR-004)."""
        # Senha sem números
        res_sem_numero = validar_numeros("SenhaForte!")
        self.assertFalse(res_sem_numero.atendido)
        self.assertEqual(res_sem_numero.codigo, CodigoCriterio.NUMEROS)
        self.assertIn("ao menos um dígito numérico", res_sem_numero.mensagem)

        # Senha com número
        res_com_numero = validar_numeros("SenhaForte1!")
        self.assertTrue(res_com_numero.atendido)
        self.assertEqual(res_com_numero.mensagem, "")

    def test_cenario_1_6_especiais(self):
        """Cenário 1.6: Senha sem caracteres especiais (FR-005)."""
        # Senha sem especiais
        res_sem_especial = validar_especiais("SenhaForte123")
        self.assertFalse(res_sem_especial.atendido)
        self.assertEqual(res_sem_especial.codigo, CodigoCriterio.ESPECIAIS)
        self.assertIn("ao menos um caractere especial", res_sem_especial.mensagem)

        # Senha com diferentes caracteres especiais
        caracteres_teste = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+", "[", "]", "{", "}", "|", ";", ":", ",", ".", "<", ">", "?", "/", "~", "`"]
        for char in caracteres_teste:
            with self.subTest(char=char):
                res = validar_especiais(f"Senha123{char}")
                self.assertTrue(res.atendido)
                self.assertEqual(res.mensagem, "")


if __name__ == "__main__":
    unittest.main()
