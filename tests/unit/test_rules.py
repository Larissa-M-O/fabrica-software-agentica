"""Testes unitários das regras estruturais e heurísticas de validação de senha (US1 e US2)."""
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
    validar_repeticao_caracteres,
    validar_senha_trivial,
    validar_sequencia_simples,
    validar_tamanho_minimo,
)


class TestRegrasEstruturais(unittest.TestCase):
    """Testes para as funções avaliadoras de regras estruturais de complexidade (US1)."""

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
        res_curta = validar_tamanho_minimo("Ab1!x")
        self.assertFalse(res_curta.atendido)
        self.assertEqual(res_curta.codigo, CodigoCriterio.TAMANHO_MINIMO)
        self.assertIn("mínimo 8 caracteres", res_curta.mensagem)

        res_limite_7 = validar_tamanho_minimo("Ab1!xyz")
        self.assertFalse(res_limite_7.atendido)

        res_limite_8 = validar_tamanho_minimo("Ab1!xyzw")
        self.assertTrue(res_limite_8.atendido)
        self.assertEqual(res_limite_8.mensagem, "")

    def test_cenario_1_3_maiusculas(self):
        """Cenário 1.3: Senha sem letras maiúsculas (FR-003)."""
        res_sem_maiuscula = validar_maiusculas("senha123!")
        self.assertFalse(res_sem_maiuscula.atendido)
        self.assertEqual(res_sem_maiuscula.codigo, CodigoCriterio.MAIUSCULAS)
        self.assertIn("ao menos uma letra maiúscula", res_sem_maiuscula.mensagem)

        res_com_maiuscula = validar_maiusculas("Senha123!")
        self.assertTrue(res_com_maiuscula.atendido)
        self.assertEqual(res_com_maiuscula.mensagem, "")

        res_unicode = validar_maiusculas("coração!123Á")
        self.assertTrue(res_unicode.atendido)

    def test_cenario_1_4_minusculas(self):
        """Cenário 1.4: Senha sem letras minúsculas (FR-002)."""
        res_sem_minuscula = validar_minusculas("SENHA123!")
        self.assertFalse(res_sem_minuscula.atendido)
        self.assertEqual(res_sem_minuscula.codigo, CodigoCriterio.MINUSCULAS)
        self.assertIn("ao menos uma letra minúscula", res_sem_minuscula.mensagem)

        res_com_minuscula = validar_minusculas("Senha123!")
        self.assertTrue(res_com_minuscula.atendido)
        self.assertEqual(res_com_minuscula.mensagem, "")

        res_unicode = validar_minusculas("CORAÇÃO!123ã")
        self.assertTrue(res_unicode.atendido)

    def test_cenario_1_5_numeros(self):
        """Cenário 1.5: Senha sem dígitos numéricos (FR-004)."""
        res_sem_numero = validar_numeros("SenhaForte!")
        self.assertFalse(res_sem_numero.atendido)
        self.assertEqual(res_sem_numero.codigo, CodigoCriterio.NUMEROS)
        self.assertIn("ao menos um dígito numérico", res_sem_numero.mensagem)

        res_com_numero = validar_numeros("SenhaForte1!")
        self.assertTrue(res_com_numero.atendido)
        self.assertEqual(res_com_numero.mensagem, "")

    def test_cenario_1_6_especiais(self):
        """Cenário 1.6: Senha sem caracteres especiais (FR-005)."""
        res_sem_especial = validar_especiais("SenhaForte123")
        self.assertFalse(res_sem_especial.atendido)
        self.assertEqual(res_sem_especial.codigo, CodigoCriterio.ESPECIAIS)
        self.assertIn("ao menos um caractere especial", res_sem_especial.mensagem)

        caracteres_teste = [
            "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+",
            "[", "]", "{", "}", "|", ";", ":", ",", ".", "<", ">", "?", "/", "~", "`"
        ]
        for char in caracteres_teste:
            with self.subTest(char=char):
                res = validar_especiais(f"Senha123{char}")
                self.assertTrue(res.atendido)
                self.assertEqual(res.mensagem, "")


class TestRegrasHeuristicas(unittest.TestCase):
    """Testes para as funções avaliadoras de padrões fracos e senhas triviais (US2)."""

    def test_cenario_2_1_senha_trivial_ou_dicionario(self):
        """Cenário 2.1: Rejeição de senhas triviais e termos conhecidos (FR-006)."""
        senhas_triviais = [
            "Password123!",
            "admin1234@",
            "qwerty123!",
            "senha123",
            "123456",
            "mudar123",
            "PASSWORD",
            "SenhaForte_admin_2026",
        ]
        for senha in senhas_triviais:
            with self.subTest(senha=senha):
                res = validar_senha_trivial(senha)
                self.assertFalse(res.atendido)
                self.assertEqual(res.codigo, CodigoCriterio.SENHA_TRIVIAL)
                self.assertIn("termos comuns ou senhas triviais", res.mensagem)

    def test_cenario_2_2_sequencias_alfanumericas_previsiveis(self):
        """Cenário 2.2: Rejeição de sequências consecutivas de 3+ caracteres (FR-007)."""
        # Sequências numéricas diretas e reversas
        self.assertFalse(validar_sequencia_simples("Abc!98765").atendido)
        self.assertFalse(validar_sequencia_simples("Senha!123x").atendido)
        self.assertFalse(validar_sequencia_simples("x321y").atendido)

        # Sequências alfabéticas diretas e reversas
        self.assertFalse(validar_sequencia_simples("Abcdef1!").atendido)
        self.assertFalse(validar_sequencia_simples("Fedcba1!").atendido)
        self.assertFalse(validar_sequencia_simples("Xyz12").atendido)
        self.assertFalse(validar_sequencia_simples("Zyx12").atendido)

        # Sequências curtas de 2 caracteres não devem violar a regra de 3+
        self.assertTrue(validar_sequencia_simples("Ab91Cd2").atendido)

        # Não deve confundir transição de tipos como sequência consecutiva
        self.assertTrue(validar_sequencia_simples("9ab!").atendido)
        self.assertTrue(validar_sequencia_simples("z01!").atendido)

    def test_cenario_2_3_repeticao_excessiva_caracteres(self):
        """Cenário 2.3: Rejeição de 3+ caracteres consecutivos idênticos (FR-008)."""
        # Repetições de letras
        res_letras = validar_repeticao_caracteres("Aaaa!1234")
        self.assertFalse(res_letras.atendido)
        self.assertEqual(res_letras.codigo, CodigoCriterio.REPETICAO_CARACTERES)
        self.assertIn("3 ou mais caracteres idênticos", res_letras.mensagem)

        # Repetições de caracteres especiais
        res_especiais = validar_repeticao_caracteres("Senha!!!12")
        self.assertFalse(res_especiais.atendido)

        # Repetições de números
        res_numeros = validar_repeticao_caracteres("Senha111!")
        self.assertFalse(res_numeros.atendido)

        # 2 caracteres consecutivos não violam
        self.assertTrue(validar_repeticao_caracteres("Aa!11!bb").atendido)

    def test_cenario_2_4_senha_robusta_sem_padroes_fracos(self):
        """Cenário 2.4: Senha combinando elementos sem padrões triviais nem repetições."""
        senha = "K9#mQ2$pL8"
        res_trivial = validar_senha_trivial(senha)
        res_seq = validar_sequencia_simples(senha)
        res_rep = validar_repeticao_caracteres(senha)

        self.assertTrue(res_trivial.atendido)
        self.assertEqual(res_trivial.mensagem, "")

        self.assertTrue(res_seq.atendido)
        self.assertEqual(res_seq.mensagem, "")

        self.assertTrue(res_rep.atendido)
        self.assertEqual(res_rep.mensagem, "")


if __name__ == "__main__":
    unittest.main()
