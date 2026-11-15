# Fase 1: Modelo de Dados (Data Model)

- **Feature:** `001-validador-senhas`
- **Etapa:** E2 — Plano Técnico (`speckit-plan`)
- **Status:** CONCLUÍDO
- **Data:** 2026-11-15
- **Autor:** Arquiteto da Fábrica de Software (`subagent-arquiteto`)

---

## 1. Visão Geral das Entidades de Domínio

O modelo de dados do motor de validação de senhas foi projetado para garantir:
1. **Tipagem Estrita e Imutabilidade:** Uso de `@dataclass(frozen=True)` e `enum.Enum` nativos do Python para assegurar imutabilidade, integridade estrutural e prevenção de efeitos colaterais.
2. **Contrato Estável e Unificado:** Atributos padronizados com os nomes ratificados no Checkpoint 1 (`is_valid`, `forca`, `criterios`, `mensagens`).
3. **Resiliência e Serialização:** Facilidade de conversão para dicionários e JSON para interoperabilidade com qualquer sistema integrador.

---

## 2. Enumerações de Domínio

### 2.1 `NivelForca`
Classificação qualitativa da robustez da senha analisada.

```python
from enum import Enum

class NivelForca(str, Enum):
    FRACA = "FRACA"
    MEDIA = "MEDIA"
    FORTE = "FORTE"
```

- **Valores Permitidos:**
  - `FRACA`: Não atende aos requisitos mínimos obrigatórios ou contém padrões fracos/triviais (sequências simples, repetições consecutivas, termos comuns).
  - `MEDIA`: Atende a todos os requisitos obrigatórios, com tamanho entre 8 e 11 caracteres.
  - `FORTE`: Atende a todos os requisitos obrigatórios, não contém padrões fracos e possui 12 ou mais caracteres com ampla diversidade de composição.

---

### 2.2 `CodigoCriterio`
Códigos canônicos para identificação mnemônica de cada regra de validação individual.

```python
class CodigoCriterio(str, Enum):
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
```

---

## 3. Estruturas de Dados Tipadas (Dataclasses)

### 3.1 `ResultadoCriterio`
Representa a avaliação detalhada de um critério específico aplicado à senha.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ResultadoCriterio:
    codigo: str
    descricao: str
    atendido: bool
    mensagem: str

    def to_dict(self) -> dict:
        return {
            "codigo": str(self.codigo),
            "descricao": self.descricao,
            "atendido": self.atendido,
            "mensagem": self.mensagem,
        }
```

#### Atributos e Regras de Validação:
| Campo | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `codigo` | `str` | Identificador mnemônico da regra (valor de `CodigoCriterio`). | `"TAMANHO_MINIMO"` |
| `descricao` | `str` | Descrição legível da finalidade da regra. | `"Comprimento mínimo de 8 caracteres"` |
| `atendido` | `bool` | `True` se a regra foi satisfeita; `False` se violada. | `False` |
| `mensagem` | `str` | Mensagem explicativa ou de orientação corretiva. | `"A senha deve conter no mínimo 8 caracteres."` |

---

### 3.2 `ResultadoValidacao`
Objeto consolidado que encapsula o diagnóstico completo emitido pelo validador.

```python
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class ResultadoValidacao:
    is_valid: bool
    forca: str
    criterios: List[ResultadoCriterio] = field(default_factory=list)
    mensagens: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "forca": str(self.forca),
            "criterios": [c.to_dict() for c in self.criterios],
            "mensagens": list(self.mensagens),
        }
```

#### Atributos e Regras de Validação:
| Campo | Tipo | Descrição | Invariante / Regra de Negócio |
|---|---|---|---|
| `is_valid` | `bool` | Indicador booleano consolidado de conformidade. | `True` se e somente se todos os critérios aplicáveis forem atendidos sem violações de segurança. |
| `forca` | `str` | Nível qualitativo de força da senha. | Deve ser `"FRACA"`, `"MEDIA"` ou `"FORTE"`. Se `is_valid == False`, obrigatoriamente `"FRACA"`. |
| `criterios` | `List[ResultadoCriterio]` | Lista de resultados individuais de cada critério avaliado. | Preserva a ordem determinística de execução das regras. |
| `mensagens` | `List[str]` | Lista consolidada de recomendações e mensagens corretivas em linguagem natural (pt-BR). | Deve ser uma lista vazia (`[]`) quando `is_valid == True`. Contém uma mensagem para cada critério não atendido quando `is_valid == False`. |

---

## 4. Invariantes de Domínio e Comportamento em Casos de Borda

1. **Invariante de Validade e Força:**
   $$\text{is\_valid} = \text{False} \implies \text{forca} = \text{"FRACA"}$$
2. **Invariante de Mensagens de Erro:**
   $$\text{is\_valid} = \text{True} \iff \text{len(mensagens)} = 0$$
3. **Imutabilidade Estrutural:**
   As instâncias de `ResultadoValidacao` e `ResultadoCriterio` são imutáveis (`frozen=True`). Nenhuma propriedade pode ser reatribuída após a instanciação.
4. **Casos de Entrada Anômala (FR-012, US4):**
   - Para entradas `None` ou tipo não string, o resultado emitido possui a seguinte conformidade:
     ```python
     ResultadoValidacao(
         is_valid=False,
         forca="FRACA",
         criterios=[
             ResultadoCriterio(
                 codigo="TIPO_ENTRADA",
                 descricao="Tipo de dado de entrada válido (string)",
                 atendido=False,
                 mensagem="O valor fornecido para validação deve ser uma cadeia de texto (string)."
             )
         ],
         mensagens=["O valor fornecido para validação deve ser uma cadeia de texto (string)."]
     )
     ```
   - Para entradas vazias ou compostas unicamente por espaços (`""` ou `"   "`):
     ```python
     ResultadoValidacao(
         is_valid=False,
         forca="FRACA",
         criterios=[
             ResultadoCriterio(
                 codigo="NAO_VAZIA",
                 descricao="Senha não vazia ou não composta unicamente por espaços",
                 atendido=False,
                 mensagem="A senha não pode ser vazia ou composta unicamente por espaços em branco."
             )
         ],
         mensagens=["A senha não pode ser vazia ou composta unicamente por espaços em branco."]
     )
     ```
