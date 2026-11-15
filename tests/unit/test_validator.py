"""Testes unitários do motor de validação e apresentação do resultado (US3, FR-009, FR-010)."""
import sys
from pathlib import Path
import unittest

# Adiciona src ao sys.path
src_path = str(Path(__file__).resolve().parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from password_validator.models import CodigoCriterio, NivelForca, ResultadoValidacao
from password_validator.validator import (
    calcular_forca,
    eh_senha_valida,
    validar_senha,
)


class TestValidator(unittest.TestCase):
    """Testes para o motor orquestrador de validação de senhas."""

    def test_cenario_3_1_senha_aprovada_forte(self):
        """Cenário 3.1: Validação completa para senha válida e forte."""
        senha = "C0mplex@Pass#2026"
        res = validar_senha(senha)

        self.assertIsInstance(res, ResultadoValidacao)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.forca, NivelForca.FORTE.value)
        self.assertEqual(res.mensagens, [])
        self.assertTrue(all(c.atendido for c in res.criterios))

        # Confirma presença de todos os critérios esperados
        codigos_presentes = [c.codigo for c in res.criterios]
        self.assertIn(CodigoCriterio.TIPO_ENTRADA, codigos_presentes)
        self.assertIn(CodigoCriterio.NAO_VAZIA, codigos_presentes)
        self.assertIn(CodigoCriterio.TAMANHO_MINIMO, codigos_presentes)
        self.assertIn(CodigoCriterio.MINUSCULAS, codigos_presentes)
        self.assertIn(CodigoCriterio.MAIUSCULAS, codigos_presentes)
        self.assertIn(CodigoCriterio.NUMEROS, codigos_presentes)
        self.assertIn(CodigoCriterio.ESPECIAIS, codigos_presentes)
        self.assertIn(CodigoCriterio.SENHA_TRIVIAL, codigos_presentes)
        self.assertIn(CodigoCriterio.SEQUENCIA_SIMPLES, codigos_presentes)
        self.assertIn(CodigoCriterio.REPETICAO_CARACTERES, codigos_presentes)

        # Serialização to_dict
        d = res.to_dict()
        self.assertTrue(d["is_valid"])
        self.assertEqual(d["forca"], "FORTE")
        self.assertEqual(d["mensagens"], [])
        self.assertEqual(len(d["criterios"]), 10)

    def test_cenario_3_2_multiplas_pendencias_com_mensagens(self):
        """Cenário 3.2: Validação de senha que viola múltiplos critérios (ex.: 'abc')."""
        senha = "abc"
        res = validar_senha(senha)

        self.assertFalse(res.is_valid)
        self.assertEqual(res.forca, NivelForca.FRACA.value)
        self.assertTrue(len(res.mensagens) > 0)

        # Mensagens esperadas para 'abc'
        mensagens_texto = " ".join(res.mensagens)
        self.assertIn("mínimo 8 caracteres", mensagens_texto)
        self.assertIn("ao menos uma letra maiúscula", mensagens_texto)
        self.assertIn("ao menos um dígito numérico", mensagens_texto)
        self.assertIn("ao menos um caractere especial", mensagens_texto)
        self.assertIn("sequências alfanuméricas", mensagens_texto)

        # Checa status individual dos critérios
        criterios_map = {c.codigo: c for c in res.criterios}
        self.assertFalse(criterios_map[CodigoCriterio.TAMANHO_MINIMO].atendido)
        self.assertFalse(criterios_map[CodigoCriterio.MAIUSCULAS].atendido)
        self.assertFalse(criterios_map[CodigoCriterio.NUMEROS].atendido)
        self.assertFalse(criterios_map[CodigoCriterio.ESPECIAIS].atendido)
        self.assertFalse(criterios_map[CodigoCriterio.SEQUENCIA_SIMPLES].atendido)
        self.assertTrue(criterios_map[CodigoCriterio.MINUSCULAS].atendido)

    def test_cenario_3_3_classificacao_forca(self):
        """Cenário 3.3: Classificação correta de força (FRACA, MEDIA, FORTE)."""
        # Senha que não atende aos requisitos -> FRACA
        res_fraca_invalida = validar_senha("SenhaForte123")  # sem especial
        self.assertFalse(res_fraca_invalida.is_valid)
        self.assertEqual(res_fraca_invalida.forca, "FRACA")

        res_fraca_trivial = validar_senha("Password123!")  # termo comum
        self.assertFalse(res_fraca_trivial.is_valid)
        self.assertEqual(res_fraca_trivial.forca, "FRACA")

        # Senha válida com comprimento entre 8 e 11 caracteres -> MEDIA
        res_media_8 = validar_senha("Ab1!kQ9#")  # exatamente 8 caracteres
        self.assertTrue(res_media_8.is_valid)
        self.assertEqual(res_media_8.forca, "MEDIA")

        res_media_11 = validar_senha("Ab1!kQ9#vW2")  # exatamente 11 caracteres
        self.assertTrue(res_media_11.is_valid)
        self.assertEqual(res_media_11.forca, "MEDIA")

        # Senha válida com comprimento >= 12 caracteres -> FORTE
        res_forte_12 = validar_senha("Ab1!kQ9#vW2$")  # exatamente 12 caracteres
        self.assertTrue(res_forte_12.is_valid)
        self.assertEqual(res_forte_12.forca, "FORTE")

        res_forte_longa = validar_senha("C0mplex@Pass#2026")  # 17 caracteres
        self.assertTrue(res_forte_longa.is_valid)
        self.assertEqual(res_forte_longa.forca, "FORTE")

    def test_eh_senha_valida_helper(self):
        """Verifica a função booleana auxiliar eh_senha_valida."""
        self.assertTrue(eh_senha_valida("C0mplex@Pass#2026"))
        self.assertTrue(eh_senha_valida("Ab1!kQ9#"))
        self.assertFalse(eh_senha_valida("abc"))
        self.assertFalse(eh_senha_valida("SenhaForte123"))
        self.assertFalse(eh_senha_valida("Password123!"))


if __name__ == "__main__":
    unittest.main()
