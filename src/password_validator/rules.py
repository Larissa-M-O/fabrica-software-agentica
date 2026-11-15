"""Regras de validação para critérios individuais de senha."""
import re
from password_validator.models import CodigoCriterio, ResultadoCriterio
from password_validator.trivial_passwords import SENHAS_TRIVIAIS

_REPETICAO_REGEX = re.compile(r"(.)\1{2,}", re.DOTALL)


def validar_tamanho_minimo(senha: str, tamanho_minimo: int = 8) -> ResultadoCriterio:
    """Valida se a senha atende ao comprimento mínimo exigido (FR-001)."""
    atendido = len(senha) >= tamanho_minimo
    mensagem = "" if atendido else f"A senha deve ter no mínimo {tamanho_minimo} caracteres."
    return ResultadoCriterio(
        codigo=CodigoCriterio.TAMANHO_MINIMO,
        descricao=f"Comprimento mínimo de {tamanho_minimo} caracteres",
        atendido=atendido,
        mensagem=mensagem,
    )


def validar_maiusculas(senha: str) -> ResultadoCriterio:
    """Valida se a senha contém ao menos uma letra maiúscula (FR-003)."""
    atendido = any(c.isupper() for c in senha)
    mensagem = "" if atendido else "A senha deve conter ao menos uma letra maiúscula."
    return ResultadoCriterio(
        codigo=CodigoCriterio.MAIUSCULAS,
        descricao="Presença de pelo menos uma letra maiúscula",
        atendido=atendido,
        mensagem=mensagem,
    )


def validar_minusculas(senha: str) -> ResultadoCriterio:
    """Valida se a senha contém ao menos uma letra minúscula (FR-002)."""
    atendido = any(c.islower() for c in senha)
    mensagem = "" if atendido else "A senha deve conter ao menos uma letra minúscula."
    return ResultadoCriterio(
        codigo=CodigoCriterio.MINUSCULAS,
        descricao="Presença de pelo menos uma letra minúscula",
        atendido=atendido,
        mensagem=mensagem,
    )


def validar_numeros(senha: str) -> ResultadoCriterio:
    """Valida se a senha contém ao menos um dígito numérico (FR-004)."""
    atendido = any(c.isdigit() for c in senha)
    mensagem = "" if atendido else "A senha deve conter ao menos um dígito numérico."
    return ResultadoCriterio(
        codigo=CodigoCriterio.NUMEROS,
        descricao="Presença de pelo menos um dígito numérico",
        atendido=atendido,
        mensagem=mensagem,
    )


def validar_especiais(senha: str) -> ResultadoCriterio:
    """Valida se a senha contém ao menos um caractere especial (FR-005)."""
    atendido = any(not c.isalnum() and not c.isspace() for c in senha)
    mensagem = "" if atendido else "A senha deve conter ao menos um caractere especial."
    return ResultadoCriterio(
        codigo=CodigoCriterio.ESPECIAIS,
        descricao="Presença de pelo menos um caractere especial",
        atendido=atendido,
        mensagem=mensagem,
    )


def validar_senha_trivial(senha: str) -> ResultadoCriterio:
    """Valida se a senha não coincide nem contém termos comuns ou triviais (FR-006)."""
    senha_lower = senha.lower()
    termo_encontrado = None

    if senha_lower in SENHAS_TRIVIAIS:
        termo_encontrado = senha_lower
    else:
        for termo in SENHAS_TRIVIAIS:
            if len(termo) >= 4 and termo in senha_lower:
                termo_encontrado = termo
                break

    atendido = termo_encontrado is None
    mensagem = (
        ""
        if atendido
        else "A senha não deve conter termos comuns ou senhas triviais conhecidas."
    )
    return ResultadoCriterio(
        codigo=CodigoCriterio.SENHA_TRIVIAL,
        descricao="Ausência de senhas conhecidas ou termos triviais",
        atendido=atendido,
        mensagem=mensagem,
    )


def validar_sequencia_simples(senha: str, limite: int = 3) -> ResultadoCriterio:
    """Valida se a senha não contém sequências alfanuméricas consecutivas de 3+ caracteres (FR-007)."""
    if len(senha) < limite:
        return ResultadoCriterio(
            codigo=CodigoCriterio.SEQUENCIA_SIMPLES,
            descricao="Ausência de sequências alfanuméricas consecutivas de 3 ou mais caracteres",
            atendido=True,
            mensagem="",
        )

    senha_lower = senha.lower()
    sequencia_encontrada = False

    for i in range(len(senha_lower) - limite + 1):
        janela = senha_lower[i : i + limite]

        # Verifica sequência numérica
        if all(c.isdigit() for c in janela):
            diffs = [ord(janela[j + 1]) - ord(janela[j]) for j in range(limite - 1)]
            if all(d == 1 for d in diffs) or all(d == -1 for d in diffs):
                sequencia_encontrada = True
                break

        # Verifica sequência alfabética ASCII
        elif all("a" <= c <= "z" for c in janela):
            diffs = [ord(janela[j + 1]) - ord(janela[j]) for j in range(limite - 1)]
            if all(d == 1 for d in diffs) or all(d == -1 for d in diffs):
                sequencia_encontrada = True
                break

    atendido = not sequencia_encontrada
    mensagem = (
        ""
        if atendido
        else "A senha não deve conter sequências alfanuméricas consecutivas simples (ex.: '123', 'abc')."
    )
    return ResultadoCriterio(
        codigo=CodigoCriterio.SEQUENCIA_SIMPLES,
        descricao="Ausência de sequências alfanuméricas consecutivas de 3 ou mais caracteres",
        atendido=atendido,
        mensagem=mensagem,
    )


def validar_repeticao_caracteres(senha: str, limite: int = 3) -> ResultadoCriterio:
    """Valida se a senha não contém repetições de 3 ou mais caracteres idênticos consecutivos (FR-008)."""
    if len(senha) < limite:
        return ResultadoCriterio(
            codigo=CodigoCriterio.REPETICAO_CARACTERES,
            descricao="Ausência de repetições de 3 ou mais caracteres idênticos consecutivos",
            atendido=True,
            mensagem="",
        )

    if limite == 3:
        tem_repeticao = bool(_REPETICAO_REGEX.search(senha))
    else:
        pattern = rf"(.)\1{{{limite - 1},}}"
        tem_repeticao = bool(re.search(pattern, senha, re.DOTALL))

    atendido = not tem_repeticao
    mensagem = (
        ""
        if atendido
        else "A senha não deve conter 3 ou mais caracteres idênticos consecutivos."
    )
    return ResultadoCriterio(
        codigo=CodigoCriterio.REPETICAO_CARACTERES,
        descricao="Ausência de repetições de 3 ou mais caracteres idênticos consecutivos",
        atendido=atendido,
        mensagem=mensagem,
    )
