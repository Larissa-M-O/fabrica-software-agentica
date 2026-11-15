"""Modelos de dados e enumerações do validador de senhas."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Sequence, Union


class NivelForca(str, Enum):
    """Classificação da força da senha."""
    FRACA = "FRACA"
    MEDIA = "MEDIA"
    FORTE = "FORTE"


class CodigoCriterio(str, Enum):
    """Códigos canônicos para identificação de regras de validação."""
    TIPO_ENTRADA = "TIPO_ENTRADA"
    NAO_VAZIA = "NAO_VAZIA"
    TAMANHO_MINIMO = "TAMANHO_MINIMO"
    MAIUSCULAS = "MAIUSCULAS"
    MINUSCULAS = "MINUSCULAS"
    NUMEROS = "NUMEROS"
    ESPECIAIS = "ESPECIAIS"
    SENHA_TRIVIAL = "SENHA_TRIVIAL"
    SEQUENCIA_SIMPLES = "SEQUENCIA_SIMPLES"
    REPETICAO_CARACTERES = "REPETICAO_CARACTERES"


@dataclass(frozen=True)
class ResultadoCriterio:
    """Resultado da avaliação de um critério individual."""
    codigo: Union[str, CodigoCriterio]
    descricao: str
    atendido: bool
    mensagem: str

    def to_dict(self) -> Dict[str, Any]:
        """Converte a instância para um dicionário serializável."""
        cod = self.codigo.value if isinstance(self.codigo, Enum) else str(self.codigo)
        return {
            "codigo": cod,
            "descricao": self.descricao,
            "atendido": self.atendido,
            "mensagem": self.mensagem,
        }


@dataclass(frozen=True)
class ResultadoValidacao:
    """Resultado consolidado da validação de uma senha."""
    is_valid: bool
    forca: Union[str, NivelForca]
    criterios: Sequence[ResultadoCriterio] = field(default_factory=list)
    mensagens: Sequence[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converte o resultado completo em um dicionário serializável."""
        forc = self.forca.value if isinstance(self.forca, Enum) else str(self.forca)
        return {
            "is_valid": self.is_valid,
            "forca": forc,
            "criterios": [c.to_dict() for c in self.criterios],
            "mensagens": list(self.mensagens),
        }
