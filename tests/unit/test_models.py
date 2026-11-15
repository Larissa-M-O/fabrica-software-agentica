"""Testes unitários dos modelos de dados e enumerações."""
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path
import unittest

# Adiciona src ao sys.path
src_path = str(Path(__file__).resolve().parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from password_validator.models import (
    CodigoCriterio,
    NivelForca,
    ResultadoCriterio,
    ResultadoValidacao,
)


class TestModels(unittest.TestCase):
    """Validação de integridade, imutabilidade e contratos dos modelos."""

    def test_nivel_forca_valores(self):
        """Verifica se os valores permitidos para NivelForca estão corretos."""
        self.assertEqual(NivelForca.FRACA.value, "FRACA")
        self.assertEqual(NivelForca.MEDIA.value, "MEDIA")
        self.assertEqual(NivelForca.FORTE.value, "FORTE")
        self.assertIsInstance(NivelForca.FRACA, str)

    def test_codigo_criterio_valores(self):
        """Verifica se os códigos canônicos estão definidos."""
        codigos_esperados = {
            "TIPO_ENTRADA",
            "NAO_VAZIA",
            "TAMANHO_MINIMO",
            "MAIUSCULAS",
            "MINUSCULAS",
            "NUMEROS",
            "ESPECIAIS",
            "SENHA_TRIVIAL",
            "SEQUENCIA_SIMPLES",
            "REPETICAO_CARACTERES",
        }
        codigos_reais = {c.value for c in CodigoCriterio}
        self.assertEqual(codigos_esperados, codigos_reais)

    def test_resultado_criterio_criacao_e_to_dict(self):
        """Testa criação e conversão para dict de ResultadoCriterio."""
        crit = ResultadoCriterio(
            codigo=CodigoCriterio.TAMANHO_MINIMO,
            descricao="Comprimento mínimo de 8 caracteres",
            atendido=True,
            mensagem="OK",
        )
        d = crit.to_dict()
        self.assertEqual(
            d,
            {
                "codigo": "TAMANHO_MINIMO",
                "descricao": "Comprimento mínimo de 8 caracteres",
                "atendido": True,
                "mensagem": "OK",
            },
        )

    def test_resultado_criterio_imutabilidade(self):
        """Garante que ResultadoCriterio é imutável (frozen=True)."""
        crit = ResultadoCriterio(
            codigo="MINUSCULAS",
            descricao="Pelo menos uma minúscula",
            atendido=False,
            mensagem="Falta minúscula",
        )
        with self.assertRaises(FrozenInstanceError):
            crit.atendido = True

    def test_resultado_validacao_criacao_e_to_dict(self):
        """Testa criação e serialização do ResultadoValidacao."""
        crit1 = ResultadoCriterio(
            codigo=CodigoCriterio.TAMANHO_MINIMO,
            descricao="Comprimento mínimo",
            atendido=True,
            mensagem="",
        )
        res = ResultadoValidacao(
            is_valid=True,
            forca=NivelForca.FORTE,
            criterios=[crit1],
            mensagens=[],
        )
        d = res.to_dict()
        self.assertEqual(d["is_valid"], True)
        self.assertEqual(d["forca"], "FORTE")
        self.assertEqual(len(d["criterios"]), 1)
        self.assertEqual(d["criterios"][0]["codigo"], "TAMANHO_MINIMO")
        self.assertEqual(d["mensagens"], [])

    def test_resultado_validacao_imutabilidade(self):
        """Garante que ResultadoValidacao é imutável (frozen=True)."""
        res = ResultadoValidacao(
            is_valid=False,
            forca=NivelForca.FRACA,
            criterios=[],
            mensagens=["Senha muito curta."],
        )
        with self.assertRaises(FrozenInstanceError):
            res.is_valid = True

    def test_resultado_validacao_defaults(self):
        """Verifica se listas padrão são inicializadas como vazias."""
        res = ResultadoValidacao(
            is_valid=False,
            forca="FRACA",
        )
        self.assertEqual(res.criterios, [])
        self.assertEqual(res.mensagens, [])


if __name__ == "__main__":
    unittest.main()
