"""Regras de validação para critérios individuais de senha."""
from password_validator.models import CodigoCriterio, ResultadoCriterio


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
