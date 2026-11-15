"""Motor principal de validação de senhas e orquestração de critérios."""
from typing import Any, List, Sequence
from password_validator.models import (
    CodigoCriterio,
    NivelForca,
    ResultadoCriterio,
    ResultadoValidacao,
)
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


def calcular_forca(senha: str, criterios: Sequence[ResultadoCriterio]) -> NivelForca:
    """
    Calcula a força qualitativa da senha com base na conformidade e comprimento (FR-009).

    - FRACA: Viola qualquer critério obrigatório ou de segurança.
    - MEDIA: Atende a todos os critérios e possui entre 8 e 11 caracteres.
    - FORTE: Atende a todos os critérios e possui 12 ou mais caracteres.
    """
    if any(not c.atendido for c in criterios):
        return NivelForca.FRACA

    if len(senha) >= 12:
        return NivelForca.FORTE

    return NivelForca.MEDIA


def validar_senha(senha: Any) -> ResultadoValidacao:
    """
    Inspeciona uma senha contra critérios estruturais e de segurança (FR-010).

    Garante execução sem lançamento de exceções para o chamador (no-throw guarantee).
    Retorna ResultadoValidacao completo e estruturado.
    """
    # Guard clause 1: Tipo de dado (FR-012, US4)
    if not isinstance(senha, str):
        criterio_tipo = ResultadoCriterio(
            codigo=CodigoCriterio.TIPO_ENTRADA,
            descricao="Tipo de dado de entrada válido (string)",
            atendido=False,
            mensagem="O valor fornecido para validação deve ser uma cadeia de texto (string).",
        )
        return ResultadoValidacao(
            is_valid=False,
            forca=NivelForca.FRACA.value,
            criterios=[criterio_tipo],
            mensagens=[criterio_tipo.mensagem],
        )

    # Guard clause 2: String vazia ou composta exclusivamente por espaços (US4)
    if len(senha.strip()) == 0:
        criterio_vazia = ResultadoCriterio(
            codigo=CodigoCriterio.NAO_VAZIA,
            descricao="Senha não vazia ou não composta unicamente por espaços",
            atendido=False,
            mensagem="A senha não pode ser vazia ou composta unicamente por espaços em branco.",
        )
        return ResultadoValidacao(
            is_valid=False,
            forca=NivelForca.FRACA.value,
            criterios=[criterio_vazia],
            mensagens=[criterio_vazia.mensagem],
        )

    # Avaliação completa dos critérios individuais
    criterios: List[ResultadoCriterio] = [
        ResultadoCriterio(
            codigo=CodigoCriterio.TIPO_ENTRADA,
            descricao="Tipo de dado de entrada válido (string)",
            atendido=True,
            mensagem="",
        ),
        ResultadoCriterio(
            codigo=CodigoCriterio.NAO_VAZIA,
            descricao="Senha não vazia ou não composta unicamente por espaços",
            atendido=True,
            mensagem="",
        ),
        validar_tamanho_minimo(senha),
        validar_minusculas(senha),
        validar_maiusculas(senha),
        validar_numeros(senha),
        validar_especiais(senha),
        validar_senha_trivial(senha),
        validar_sequencia_simples(senha),
        validar_repeticao_caracteres(senha),
    ]

    is_valid = all(c.atendido for c in criterios)
    forca = calcular_forca(senha, criterios)
    mensagens = [c.mensagem for c in criterios if not c.atendido and c.mensagem]

    return ResultadoValidacao(
        is_valid=is_valid,
        forca=forca.value,
        criterios=criterios,
        mensagens=mensagens,
    )


def eh_senha_valida(senha: Any) -> bool:
    """
    Função utilitária simplificada (helper) que retorna True se a senha for válida;
    retorna False caso contrário (incluindo entradas inválidas ou não-texto).
    """
    return validar_senha(senha).is_valid
