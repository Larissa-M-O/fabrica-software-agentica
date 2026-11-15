"""Testes de Aceite e Integração Ponta a Ponta (E6 - QA).

Rastreabilidade:
- US1 [P1] / FR-001 a FR-005: Requisitos estruturais de complexidade.
- US2 [P1] / FR-006 a FR-008: Detecção de termos triviais, sequências e repetições.
- US3 [P2] / FR-009 a FR-010: Relatório estruturado, cálculo de força e invariantes.
- US4 [P3] / FR-011 a FR-012: Passphrases, resiliência de tipos e casos de borda.
- SC-001 a SC-005: Critérios de Sucesso e Requisitos Não Funcionais.
"""
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import time
import unittest

# Adiciona src ao sys.path para importação do módulo de produção
SRC_PATH = str(Path(__file__).resolve().parent.parent.parent / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from password_validator import (  # noqa: E402
    CodigoCriterio,
    NivelForca,
    ResultadoCriterio,
    ResultadoValidacao,
    eh_senha_valida,
    validar_senha,
)


class TestAceiteUS1ComplexidadeEstrutural(unittest.TestCase):
    """Cenários de Aceite da História US1: Validação de Requisitos Estruturais."""

    def test_cenario_1_1_senha_atende_todos_requisitos_estruturais(self):
        """Cenário 1.1: Senha com 10 caracteres contendo maiúsculas, minúsculas, números e especiais."""
        senha_valida = "Ab1!kQ9#vW"
        resultado = validar_senha(senha_valida)

        self.assertIsInstance(resultado, ResultadoValidacao)
        self.assertTrue(resultado.is_valid, "Senha que atende a todos os critérios deve ser válida")
        self.assertEqual(resultado.mensagens, [], "Senha válida não deve conter mensagens de erro")

        # Verifica se todos os critérios estruturais foram atendidos
        criterios_dict = {c.codigo: c.atendido for c in resultado.criterios}
        self.assertTrue(criterios_dict[CodigoCriterio.TAMANHO_MINIMO])
        self.assertTrue(criterios_dict[CodigoCriterio.MINUSCULAS])
        self.assertTrue(criterios_dict[CodigoCriterio.MAIUSCULAS])
        self.assertTrue(criterios_dict[CodigoCriterio.NUMEROS])
        self.assertTrue(criterios_dict[CodigoCriterio.ESPECIAIS])

        # Verificação do helper booleano
        self.assertTrue(eh_senha_valida(senha_valida))

    def test_cenario_1_2_senha_comprimento_inferior_minimo(self):
        """Cenário 1.2: Senhas com menos de 8 caracteres devem falhar no critério de tamanho (FR-001)."""
        casos_curtos = [
            ("Ab1!", 4),
            ("Ab1!x", 5),
            ("Ab1!xY", 6),
            ("Ab1!xYz", 7),  # Limite de fronteira imediatamente inferior a 8
        ]
        for senha, tamanho in casos_curtos:
            with self.subTest(senha=senha, tamanho=tamanho):
                resultado = validar_senha(senha)
                self.assertFalse(resultado.is_valid)
                self.assertEqual(resultado.forca, NivelForca.FRACA.value)

                crit_tamanho = next(
                    c for c in resultado.criterios if c.codigo == CodigoCriterio.TAMANHO_MINIMO
                )
                self.assertFalse(crit_tamanho.atendido)
                self.assertIn("no mínimo 8 caracteres", crit_tamanho.mensagem)
                self.assertTrue(
                    any("no mínimo 8 caracteres" in msg for msg in resultado.mensagens)
                )
                self.assertFalse(eh_senha_valida(senha))

    def test_cenario_1_3_senha_sem_letras_maiusculas(self):
        """Cenário 1.3: Senha sem letras maiúsculas deve falhar em MAIUSCULAS (FR-003)."""
        senha = "senha123!#abc"
        resultado = validar_senha(senha)

        self.assertFalse(resultado.is_valid)
        self.assertEqual(resultado.forca, NivelForca.FRACA.value)

        crit_mai = next(c for c in resultado.criterios if c.codigo == CodigoCriterio.MAIUSCULAS)
        self.assertFalse(crit_mai.atendido)
        self.assertIn("ao menos uma letra maiúscula", crit_mai.mensagem)
        self.assertFalse(eh_senha_valida(senha))

    def test_cenario_1_4_senha_sem_letras_minusculas(self):
        """Cenário 1.4: Senha sem letras minúsculas deve falhar em MINUSCULAS (FR-002)."""
        senha = "SENHA123!#ABC"
        resultado = validar_senha(senha)

        self.assertFalse(resultado.is_valid)
        self.assertEqual(resultado.forca, NivelForca.FRACA.value)

        crit_min = next(c for c in resultado.criterios if c.codigo == CodigoCriterio.MINUSCULAS)
        self.assertFalse(crit_min.atendido)
        self.assertIn("ao menos uma letra minúscula", crit_min.mensagem)
        self.assertFalse(eh_senha_valida(senha))

    def test_cenario_1_5_senha_sem_digitos_numericos(self):
        """Cenário 1.5: Senha sem dígitos numéricos deve falhar em NUMEROS (FR-004)."""
        senha = "SenhaForte!Muito"
        resultado = validar_senha(senha)

        self.assertFalse(resultado.is_valid)
        self.assertEqual(resultado.forca, NivelForca.FRACA.value)

        crit_num = next(c for c in resultado.criterios if c.codigo == CodigoCriterio.NUMEROS)
        self.assertFalse(crit_num.atendido)
        self.assertIn("ao menos um dígito numérico", crit_num.mensagem)
        self.assertFalse(eh_senha_valida(senha))

    def test_cenario_1_6_senha_sem_caracteres_especiais(self):
        """Cenário 1.6: Senha sem caracteres especiais deve falhar em ESPECIAIS (FR-005)."""
        senha = "SenhaForte12345"
        resultado = validar_senha(senha)

        self.assertFalse(resultado.is_valid)
        self.assertEqual(resultado.forca, NivelForca.FRACA.value)

        crit_esp = next(c for c in resultado.criterios if c.codigo == CodigoCriterio.ESPECIAIS)
        self.assertFalse(crit_esp.atendido)
        self.assertIn("ao menos um caractere especial", crit_esp.mensagem)
        self.assertFalse(eh_senha_valida(senha))


class TestAceiteUS2PadroesTriviaisESequencias(unittest.TestCase):
    """Cenários de Aceite da História US2: Identificação e Rejeição de Senhas Triviais."""

    def test_cenario_2_1_senhas_triviais_e_dicionario(self):
        """Cenário 2.1: Senhas pertencentes ou contendo termos da lista trivial (FR-006)."""
        senhas_triviais = [
            "Password123!",
            "admin1234@",
            "qwerty123!",
            "123456!Aa",
            "Mudar123!",
            "SuperSenha1!",
        ]
        for senha in senhas_triviais:
            with self.subTest(senha=senha):
                resultado = validar_senha(senha)
                self.assertFalse(resultado.is_valid)
                self.assertEqual(resultado.forca, NivelForca.FRACA.value)

                crit_trivial = next(
                    c for c in resultado.criterios if c.codigo == CodigoCriterio.SENHA_TRIVIAL
                )
                self.assertFalse(crit_trivial.atendido)
                self.assertIn("termos comuns ou senhas triviais", crit_trivial.mensagem)
                self.assertFalse(eh_senha_valida(senha))

    def test_cenario_2_2_sequencias_alfanumericas_previsiveis_diretas_e_reversas(self):
        """Cenário 2.2: Sequências alfanuméricas consecutivas simples >= 3 caracteres (FR-007)."""
        casos_sequencias = [
            ("Senha!123xK", "123 direta"),
            ("Abc!98765#", "987 reversa"),
            ("Test#321!Wq", "321 reversa"),
            ("Chave!xyz#9K", "xyz direta"),
            ("Porta$cba#1M", "cba reversa"),
            ("Segredo!456@W", "456 direta"),
        ]
        for senha, descricao in casos_sequencias:
            with self.subTest(senha=senha, descricao=descricao):
                resultado = validar_senha(senha)
                self.assertFalse(resultado.is_valid, f"Deveria falhar para sequência: {descricao}")
                self.assertEqual(resultado.forca, NivelForca.FRACA.value)

                crit_seq = next(
                    c for c in resultado.criterios if c.codigo == CodigoCriterio.SEQUENCIA_SIMPLES
                )
                self.assertFalse(crit_seq.atendido)
                self.assertIn("sequências alfanuméricas consecutivas", crit_seq.mensagem)
                self.assertFalse(eh_senha_valida(senha))

    def test_cenario_2_3_repeticoes_excessivas_de_caracteres_identicos(self):
        """Cenário 2.3: Repetição de 3 ou mais caracteres idênticos consecutivos (FR-008)."""
        casos_repeticao = [
            ("Aaaa!1234#K", "letras minúsculas 'aaaa'"),
            ("Senha!!!12W", "símbolos especiais '!!!'"),
            ("Pass111#2026W", "dígitos '111'"),
            ("ZZZ#chave9!k", "letras maiúsculas 'ZZZ'"),
        ]
        for senha, descricao in casos_repeticao:
            with self.subTest(senha=senha, descricao=descricao):
                resultado = validar_senha(senha)
                self.assertFalse(resultado.is_valid, f"Deveria falhar para repetição: {descricao}")
                self.assertEqual(resultado.forca, NivelForca.FRACA.value)

                crit_rep = next(
                    c for c in resultado.criterios if c.codigo == CodigoCriterio.REPETICAO_CARACTERES
                )
                self.assertFalse(crit_rep.atendido)
                self.assertIn("caracteres idênticos consecutivos", crit_rep.mensagem)
                self.assertFalse(eh_senha_valida(senha))

    def test_cenario_2_4_senha_variada_sem_padroes_triviais(self):
        """Cenário 2.4: Senha com ampla variedade e sem padrões fracos deve ser aprovada."""
        senha_robusta = "K9#mQ2$pL8"
        resultado = validar_senha(senha_robusta)

        self.assertTrue(resultado.is_valid)
        self.assertEqual(resultado.mensagens, [])

        crit_trivial = next(
            c for c in resultado.criterios if c.codigo == CodigoCriterio.SENHA_TRIVIAL
        )
        crit_seq = next(
            c for c in resultado.criterios if c.codigo == CodigoCriterio.SEQUENCIA_SIMPLES
        )
        crit_rep = next(
            c for c in resultado.criterios if c.codigo == CodigoCriterio.REPETICAO_CARACTERES
        )
        self.assertTrue(crit_trivial.atendido)
        self.assertTrue(crit_seq.atendido)
        self.assertTrue(crit_rep.atendido)
        self.assertTrue(eh_senha_valida(senha_robusta))


class TestAceiteUS3RelatorioEstruturadoEForca(unittest.TestCase):
    """Cenários de Aceite da História US3: Apresentação do Resultado Estruturado."""

    def test_cenario_3_1_contrato_completo_para_senha_forte(self):
        """Cenário 3.1: Validação com feedback detalhado para senha aprovada (FR-010)."""
        senha = "C0mplex@Pass#2026"
        resultado = validar_senha(senha)

        # Contrato tipado
        self.assertTrue(resultado.is_valid)
        self.assertEqual(resultado.forca, "FORTE")
        self.assertEqual(resultado.mensagens, [])
        self.assertEqual(len(resultado.criterios), 10)

        # Serialização via to_dict
        dados = resultado.to_dict()
        self.assertIsInstance(dados, dict)
        self.assertEqual(dados["is_valid"], True)
        self.assertEqual(dados["forca"], "FORTE")
        self.assertEqual(dados["mensagens"], [])
        self.assertIsInstance(dados["criterios"], list)
        self.assertEqual(len(dados["criterios"]), 10)

        # Valida campos de cada critério serializado
        for c in dados["criterios"]:
            self.assertIn("codigo", c)
            self.assertIn("descricao", c)
            self.assertIn("atendido", c)
            self.assertIn("mensagem", c)
            self.assertTrue(c["atendido"])
            self.assertEqual(c["mensagem"], "")

    def test_cenario_3_2_multiplas_pendencias_com_mensagens_corretivas(self):
        """Cenário 3.2: Senha com múltiplos problemas deve consolidar mensagens corretivas em pt-BR."""
        senha = "abc"
        resultado = validar_senha(senha)

        self.assertFalse(resultado.is_valid)
        self.assertEqual(resultado.forca, "FRACA")
        self.assertTrue(len(resultado.mensagens) >= 4)

        # Verifica presença de mensagens essenciais em linguagem natural
        mensagens_texto = " ".join(resultado.mensagens)
        self.assertIn("no mínimo 8 caracteres", mensagens_texto)
        self.assertIn("ao menos uma letra maiúscula", mensagens_texto)
        self.assertIn("ao menos um dígito numérico", mensagens_texto)
        self.assertIn("ao menos um caractere especial", mensagens_texto)
        self.assertIn("sequências alfanuméricas", mensagens_texto)

    def test_cenario_3_3_limiares_de_classificacao_de_forca(self):
        """Cenário 3.3: Classificação correta nos limiares 8, 11 e 12 caracteres (FR-009)."""
        # Limiar inferior da média: exatamente 8 caracteres válidos
        res_8 = validar_senha("Ab1!kQ9#")
        self.assertTrue(res_8.is_valid)
        self.assertEqual(res_8.forca, "MEDIA")

        # Limiar superior da média: exatamente 11 caracteres válidos
        res_11 = validar_senha("Ab1!kQ9#vW2")
        self.assertTrue(res_11.is_valid)
        self.assertEqual(res_11.forca, "MEDIA")

        # Limiar inferior da forte: exatamente 12 caracteres válidos
        res_12 = validar_senha("Ab1!kQ9#vW2$")
        self.assertTrue(res_12.is_valid)
        self.assertEqual(res_12.forca, "FORTE")

        # Senha muito longa e complexa: >= 12 caracteres válidos
        res_longa = validar_senha("C0mplex@Pass#2026!Forte")
        self.assertTrue(res_longa.is_valid)
        self.assertEqual(res_longa.forca, "FORTE")

        # Qualquer falha obrigatória força nível para FRACA
        res_falha_8 = validar_senha("ab1!kq9#")  # 8 chars sem maiúscula
        self.assertFalse(res_falha_8.is_valid)
        self.assertEqual(res_falha_8.forca, "FRACA")

        res_falha_15 = validar_senha("SenhaLongaSemNumero!")  # 20 chars sem número
        self.assertFalse(res_falha_15.is_valid)
        self.assertEqual(res_falha_15.forca, "FRACA")

    def test_invariantes_de_dominio_resultado(self):
        """Verifica as invariantes formais do modelo de dados."""
        # Invariante 1: is_valid == False => forca == 'FRACA'
        for caso_invalido in ["", "   ", "abc", "Password123!", None, 99999]:
            res = validar_senha(caso_invalido)
            self.assertFalse(res.is_valid)
            self.assertEqual(res.forca, "FRACA")

        # Invariante 2: is_valid == True <=> len(mensagens) == 0
        for caso_valido in ["Ab1!kQ9#", "Ab1!kQ9#vW2$", "C0mplex@Pass#2026"]:
            res = validar_senha(caso_valido)
            self.assertTrue(res.is_valid)
            self.assertEqual(len(res.mensagens), 0)


class TestAceiteUS4ResilienciaEntradasECasosBorda(unittest.TestCase):
    """Cenários de Aceite da História US4: Resiliência de Entradas e Casos de Borda."""

    def test_cenario_4_1_entradas_nulas_e_tipos_invalidos_sem_excecao(self):
        """Cenário 4.1: Entradas nulas e não textuais retornam resultado estruturado (FR-012)."""
        entradas_heterogeneas = [
            None,
            12345678,
            3.14159,
            True,
            False,
            ["senha"],
            {"chave": "valor"},
            ("tupla", 1),
            object(),
            b"bytes_password",
        ]
        for entrada in entradas_heterogeneas:
            with self.subTest(entrada=entrada, tipo=type(entrada).__name__):
                res = validar_senha(entrada)
                self.assertIsInstance(res, ResultadoValidacao)
                self.assertFalse(res.is_valid)
                self.assertEqual(res.forca, "FRACA")
                self.assertTrue(len(res.mensagens) > 0)
                self.assertIn("cadeia de texto (string)", res.mensagens[0])
                self.assertEqual(res.criterios[0].codigo, CodigoCriterio.TIPO_ENTRADA)
                self.assertFalse(res.criterios[0].atendido)
                self.assertFalse(eh_senha_valida(entrada))

    def test_cenario_4_2_entradas_vazias_e_somente_espacos(self):
        """Cenário 4.2: Entrada vazia ou contendo exclusivamente espaços em branco."""
        entradas_vazias = ["", " ", "   ", "\t", "\n", "\r\n", "  \t \n  "]
        for entrada in entradas_vazias:
            with self.subTest(entrada=repr(entrada)):
                res = validar_senha(entrada)
                self.assertFalse(res.is_valid)
                self.assertEqual(res.forca, "FRACA")
                self.assertTrue(len(res.mensagens) > 0)
                self.assertIn("não pode ser vazia", res.mensagens[0])
                self.assertEqual(res.criterios[0].codigo, CodigoCriterio.NAO_VAZIA)
                self.assertFalse(res.criterios[0].atendido)
                self.assertFalse(eh_senha_valida(entrada))

    def test_cenario_4_3_passphrases_com_espacos_internos(self):
        """Cenário 4.3: Passphrases com espaços intermediários válidos preservados (FR-011)."""
        frases = [
            "Cavalo Azul Salta @981",
            "Mesa Verde Segura #457",
            "O Vento Sopra Forte !2026",
        ]
        for frase in frases:
            with self.subTest(frase=frase):
                res = validar_senha(frase)
                self.assertTrue(res.is_valid)
                self.assertEqual(res.forca, "FORTE")
                self.assertEqual(res.mensagens, [])
                self.assertTrue(eh_senha_valida(frase))

                # Confirma que o comprimento preservou os espaços internos
                crit_tam = next(
                    c for c in res.criterios if c.codigo == CodigoCriterio.TAMANHO_MINIMO
                )
                self.assertTrue(crit_tam.atendido)

    def test_cenario_4_4_suporte_caracteres_unicode_e_acentuacao(self):
        """Cenário 4.4: Suporte a caracteres acentuados e símbolos Unicode válidos."""
        senhas_unicode = [
            "Coração!Seguro#2026",
            "Avião#Rápido!842",
            "Esperança$Forte&2026",
        ]
        for senha in senhas_unicode:
            with self.subTest(senha=senha):
                res = validar_senha(senha)
                self.assertTrue(res.is_valid)
                self.assertEqual(res.forca, "FORTE")
                self.assertEqual(res.mensagens, [])
                self.assertTrue(eh_senha_valida(senha))

    def test_passphrase_longa_limite_128_caracteres(self):
        """Caso de borda: Passphrase com 128 caracteres exatos processada com integridade."""
        base = "PassphraseLongaSegura@2026"
        # Constrói frase de 128 caracteres
        longa = (base * 5)[:128]
        self.assertEqual(len(longa), 128)

        res = validar_senha(longa)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.forca, "FORTE")
        self.assertEqual(res.mensagens, [])


class TestAceiteRequisitosNaoFuncionais(unittest.TestCase):
    """Critérios de Sucesso e Requisitos Não Funcionais (SC-001 a SC-005)."""

    def test_sc001_zero_dependencias_externas(self):
        """SC-001: 100% de dependências estritamente contidas na biblioteca padrão do Python."""
        modulos_permitidos = {
            "dataclasses",
            "enum",
            "re",
            "typing",
            "unittest",
            "string",
            "sys",
            "pathlib",
            "time",
            "collections",
            "abc",
        }
        import password_validator
        import password_validator.models
        import password_validator.rules
        import password_validator.trivial_passwords
        import password_validator.validator

        modulos_projeto = [
            password_validator,
            password_validator.models,
            password_validator.rules,
            password_validator.trivial_passwords,
            password_validator.validator,
        ]

        # Inspeciona módulos carregados por password_validator
        for mod in modulos_projeto:
            for nome_attr, attr in vars(mod).items():
                if hasattr(attr, "__module__") and attr.__module__:
                    modulo_origem = attr.__module__.split(".")[0]
                    if modulo_origem != "password_validator" and not modulo_origem.startswith("_"):
                        self.assertIn(
                            modulo_origem,
                            modulos_permitidos,
                            f"Módulo externo não permitido detectado: {modulo_origem} em {mod.__name__}",
                        )

    def test_sc002_desempenho_abaixo_5ms_estatistico(self):
        """SC-002: Tempo de validação inferior a 5 milissegundos para senhas de até 128 caracteres."""
        amostras = [
            "Ab1!kQ9#",  # 8 caracteres
            "C0mplex@Pass#2026",  # 17 caracteres
            ("PassphraseLongaSegura@2026" * 5)[:128],  # 128 caracteres
            "Password123!",  # Trivial
            "Senha!123xK",  # Sequência
            "Aaaa!1234#K",  # Repetição
        ]

        # Executa 300 validações para cada amostra e mede latência máxima e média
        for amostra in amostras:
            tempos = []
            for _ in range(300):
                t0 = time.perf_counter()
                validar_senha(amostra)
                t1 = time.perf_counter()
                tempos.append(t1 - t0)

            tempo_medio_ms = (sum(tempos) / len(tempos)) * 1000.0
            tempo_max_ms = max(tempos) * 1000.0

            # Meta: tempo médio < 1.0 ms e tempo máximo < 5.0 ms
            self.assertLess(
                tempo_medio_ms,
                1.0,
                f"Tempo médio excedeu 1 ms para tamanho {len(amostra)}: {tempo_medio_ms:.4f} ms",
            )
            self.assertLess(
                tempo_max_ms,
                5.0,
                f"Tempo máximo excedeu 5 ms para tamanho {len(amostra)}: {tempo_max_ms:.4f} ms",
            )

    def test_sc003_determinismo_e_imutabilidade(self):
        """SC-003: Validação estritamente determinística e estruturas de dados imutáveis."""
        senha = "K9#mQ2$pL8"

        # Teste de determinismo: 50 execuções produzem exatamente o mesmo resultado
        referencia = validar_senha(senha).to_dict()
        for _ in range(50):
            self.assertEqual(validar_senha(senha).to_dict(), referencia)

        # Teste de imutabilidade: classes decoradas com frozen=True não permitem reatribuição
        resultado = validar_senha(senha)
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            resultado.is_valid = False  # type: ignore

        with self.assertRaises((FrozenInstanceError, AttributeError)):
            resultado.forca = "FRACA"  # type: ignore

        criterio = resultado.criterios[0]
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            criterio.atendido = False  # type: ignore

    def test_sc005_compreensibilidade_mensagens_ptbr(self):
        """SC-005: Mensagens explicativas e corretivas claras em língua portuguesa (pt-BR)."""
        casos = [
            ("abc", "no mínimo 8 caracteres"),
            ("senha123!", "ao menos uma letra maiúscula"),
            ("SENHA123!", "ao menos uma letra minúscula"),
            ("SenhaForte!", "ao menos um dígito numérico"),
            ("SenhaForte123", "ao menos um caractere especial"),
            ("Password123!", "termos comuns ou senhas triviais"),
            ("Senha!123x", "sequências alfanuméricas consecutivas"),
            ("Senha!!!12", "caracteres idênticos consecutivos"),
            (None, "cadeia de texto (string)"),
            ("   ", "não pode ser vazia ou composta unicamente por espaços"),
        ]
        for entrada, trecho_esperado in casos:
            with self.subTest(entrada=repr(entrada)):
                res = validar_senha(entrada)
                self.assertFalse(res.is_valid)
                mensagens_unificadas = " ".join(res.mensagens)
                self.assertIn(
                    trecho_esperado,
                    mensagens_unificadas,
                    f"Mensagem esperada '{trecho_esperado}' não encontrada em '{mensagens_unificadas}'",
                )


if __name__ == "__main__":
    unittest.main()
