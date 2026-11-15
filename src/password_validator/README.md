# Validador de Senhas (`password_validator`)

Motor determinístico, modular e resiliente de validação e avaliação de força de senhas, desenvolvido exclusivamente com a biblioteca padrão do Python (**Python Standard Library**), sem qualquer dependência externa (`pip`), banco de dados ou requisição de rede.

---

## 1. Características Principais

- **Zero Dependências Externas (SC-001):** Utiliza 100% Python Standard Library (`dataclasses`, `enum`, `re`, `typing`, `unittest`).
- **Garantia de Não Lançamento de Exceções (*No-Throw Guarantee*, FR-012):** Nunca lança exceções não tratadas (`TypeError`, `ValueError`, etc.) para o chamador, mesmo para entradas `None` ou tipos arbitrários.
- **Alta Eficiência e Baixa Latência (SC-002):** Algoritmos com complexidade temporal linear $O(n)$ garantem tempo de resposta inferior a 1 milissegundo para senhas usuais.
- **Imutabilidade e Thread-Safety (SC-003):** Estruturas `@dataclass(frozen=True)` e catálogo em memória imutável (`frozenset`).
- **Suporte a Passphrases e Unicode (FR-011):** Preservação de espaços internos em frases secretas e suporte pleno a caracteres acentuados.

---

## 2. Instalação e Requisitos

- **Python:** 3.10 ou superior.
- Não requer instalação via gerenciador de pacotes (`pip`). O módulo pode ser incluído diretamente na árvore de código do projeto.

---

## 3. Uso da API Pública

### 3.1 Importação

```python
from password_validator import (
    validar_senha,
    eh_senha_valida,
    ResultadoValidacao,
    ResultadoCriterio,
    NivelForca,
    CodigoCriterio,
)
```

### 3.2 Validação Detalhada com Diagnóstico Completo

```python
resultado = validar_senha("C0mplex@Pass#2026")

print("Válida:", resultado.is_valid)       # True
print("Força:", resultado.forca)           # "FORTE"
print("Mensagens:", resultado.mensagens)   # []

# Conversão direta para dicionário serializável em JSON
dados_dict = resultado.to_dict()
```

### 3.3 Checagem Rápida (Helper Booleano)

```python
if eh_senha_valida("Ab1!kQ9#"):
    print("Senha aceita!")
else:
    print("Senha rejeitada!")
```

### 3.4 Tratamento Resiliente de Entradas Inválidas

```python
resultado_nulo = validar_senha(None)
print(resultado_nulo.is_valid)   # False
print(resultado_nulo.forca)      # "FRACA"
print(resultado_nulo.mensagens)  # ["O valor fornecido para validação deve ser uma cadeia de texto (string)."]

resultado_vazio = validar_senha("   ")
print(resultado_vazio.is_valid)   # False
print(resultado_vazio.mensagens)  # ["A senha não pode ser vazia ou composta unicamente por espaços em branco."]
```

---

## 4. Tabela de Critérios Avaliados

| Código Canônico (`CodigoCriterio`) | Descrição do Critério | Requisito |
|---|---|:---:|
| `TIPO_ENTRADA` | Validação de tipo de dado textual (`isinstance(senha, str)`). | FR-012 |
| `NAO_VAZIA` | Rejeição de senhas vazias ou compostas unicamente por espaços. | FR-011 |
| `TAMANHO_MINIMO` | Comprimento mínimo de 8 caracteres. | FR-001 |
| `MINUSCULAS` | Presença de pelo menos uma letra minúscula (suporte a Unicode). | FR-002 |
| `MAIUSCULAS` | Presença de pelo menos uma letra maiúscula (suporte a Unicode). | FR-003 |
| `NUMEROS` | Presença de pelo menos um dígito numérico decimal (`0-9`). | FR-004 |
| `ESPECIAIS` | Presença de pelo menos um caractere especial/símbolo de pontuação. | FR-005 |
| `SENHA_TRIVIAL` | Ausência de senhas conhecidas de dicionário ou termos comuns vulneráveis. | FR-006 |
| `SEQUENCIA_SIMPLES` | Ausência de sequências alfanuméricas consecutivas de 3+ caracteres (diretas ou reversas). | FR-007 |
| `REPETICAO_CARACTERES` | Ausência de 3 ou mais caracteres consecutivos idênticos. | FR-008 |

---

## 5. Classificação de Força (`NivelForca`)

- **`FRACA`:** A senha violou qualquer critério estrutural ou de segurança obrigatório.
- **`MEDIA`:** A senha atendeu a todos os critérios e possui comprimento entre 8 e 11 caracteres.
- **`FORTE`:** A senha atendeu a todos os critérios e possui comprimento igual ou superior a 12 caracteres.
