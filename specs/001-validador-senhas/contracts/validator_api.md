# Contrato da API Pública do Validador de Senhas

- **Feature:** `001-validador-senhas`
- **Etapa:** E2 — Plano Técnico (`speckit-plan`)
- **Status:** CONCLUÍDO
- **Data:** 2026-11-15
- **Autor:** Arquiteto da Fábrica de Software (`subagent-arquiteto`)

---

## 1. Identificação do Módulo e Pacote

- **Pacote Python:** `password_validator`
- **Ponto de Importação:** `from password_validator import validar_senha, eh_senha_valida, ResultadoValidacao, NivelForca`
- **Dependências Externas:** Nenhuma (100% Python Standard Library).

---

## 2. Assinatura das Funções Públicas

### 2.1 `validar_senha`

Função principal de inspeção e avaliação detalhada da senha.

```python
def validar_senha(senha: Any) -> ResultadoValidacao:
    """
    Inspeciona uma senha contra critérios estruturais e de segurança, emitindo
    um relatório detalhado de conformidade, classificação de força e mensagens corretivas.

    Garante execução segura sem levantamento de exceções (No-throw guarantee).
    Para tipos inválidos ou None, retorna um ResultadoValidacao com is_valid=False.

    :param senha: Valor a ser validado (esperado str, mas tolera qualquer tipo com tratamento seguro).
    :return: ResultadoValidacao contendo is_valid, forca, criterios e mensagens.
    """
```

### 2.2 `eh_senha_valida`

Função utilitária simplificada (helper) para cenários onde a aplicação chamadora necessita apenas de um booleano direto.

```python
def eh_senha_valida(senha: Any) -> bool:
    """
    Retorna True se a senha atende plenamente a todos os critérios e regras de segurança;
    retorna False caso contrário (incluindo entradas inválidas, vazias ou não-texto).

    :param senha: Valor a ser validado.
    :return: bool indicando se a senha é válida.
    """
```

---

## 3. Garantias Contratuais e Tratamento de Exceções

1. **Garantia de Não Lançamento de Exceções (*No-Throw Guarantee*):**
   A função `validar_senha` **nunca** lança exceções não tratadas (`TypeError`, `ValueError`, `AttributeError`, etc.) para o chamador, mesmo quando submetida a valores como `None`, inteiros, dicionários, listas ou strings com caracteres malformados.
2. **Determinismo e Idempotência:**
   Para uma mesma entrada $S$, `validar_senha(S)` produzirá rigorosamente o mesmo resultado estruturado em qualquer momento da execução.
3. **Imutabilidade e Isolamento de Estado:**
   O pacote não armazena variáveis mutáveis em nível de módulo nem compartilha coleções que possam ser corrompidas entre threads.
4. **Desempenho Estável:**
   Tempo médio de processamento por senha inferior a 1 milissegundo (limite estipulado pelo critério SC-002: < 5 ms).

---

## 4. Esquema de Saída Serializada (JSON / Dicionário)

Quando o método `to_dict()` for invocado no objeto retornado, o esquema JSON gerado segue estritamente a especificação:

```json
{
  "type": "object",
  "properties": {
    "is_valid": { "type": "boolean" },
    "forca": {
      "type": "string",
      "enum": ["FRACA", "MEDIA", "FORTE"]
    },
    "criterios": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "codigo": { "type": "string" },
          "descricao": { "type": "string" },
          "atendido": { "type": "boolean" },
          "mensagem": { "type": "string" }
        },
        "required": ["codigo", "descricao", "atendido", "mensagem"]
      }
    },
    "mensagens": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["is_valid", "forca", "criterios", "mensagens"]
}
```

---

## 5. Exemplos de Troca de Dados

### 5.1 Exemplo: Senha Válida Forte
**Entrada:** `"C0mplex@Pass#2026"`

**Retorno Python (`ResultadoValidacao`):**
```python
ResultadoValidacao(
    is_valid=True,
    forca="FORTE",
    criterios=[
        ResultadoCriterio(codigo="TIPO_ENTRADA", descricao="Tipo de dado de entrada válido (string)", atendido=True, mensagem=""),
        ResultadoCriterio(codigo="NAO_VAZIA", descricao="Senha não vazia ou não composta unicamente por espaços", atendido=True, mensagem=""),
        ResultadoCriterio(codigo="TAMANHO_MINIMO", descricao="Comprimento mínimo de 8 caracteres", atendido=True, mensagem=""),
        ResultadoCriterio(codigo="MINUSCULAS", descricao="Presença de pelo menos uma letra minúscula", atendido=True, mensagem=""),
        ResultadoCriterio(codigo="MAIUSCULAS", descricao="Presença de pelo menos uma letra maiúscula", atendido=True, mensagem=""),
        ResultadoCriterio(codigo="NUMEROS", descricao="Presença de pelo menos um dígito numérico", atendido=True, mensagem=""),
        ResultadoCriterio(codigo="ESPECIAIS", descricao="Presença de pelo menos um caractere especial", atendido=True, mensagem=""),
        ResultadoCriterio(codigo="SENHA_TRIVIAL", descricao="Ausência de senhas conhecidas ou termos triviais", atendido=True, mensagem=""),
        ResultadoCriterio(codigo="SEQUENCIA_SIMPLES", descricao="Ausência de sequências alfanuméricas consecutivas de 3 ou mais caracteres", atendido=True, mensagem=""),
        ResultadoCriterio(codigo="REPETICAO_CARACTERES", descricao="Ausência de repetições de 3 ou mais caracteres idênticos consecutivos", atendido=True, mensagem="")
    ],
    mensagens=[]
)
```

### 5.2 Exemplo: Senha Inválida (Múltiplas Violações)
**Entrada:** `"abc"`

**Retorno Python (`ResultadoValidacao`):**
```python
ResultadoValidacao(
    is_valid=False,
    forca="FRACA",
    criterios=[
        ResultadoCriterio(codigo="TAMANHO_MINIMO", descricao="Comprimento mínimo de 8 caracteres", atendido=False, mensagem="A senha deve ter no mínimo 8 caracteres."),
        ResultadoCriterio(codigo="MAIUSCULAS", descricao="Presença de pelo menos uma letra maiúscula", atendido=False, mensagem="A senha deve conter ao menos uma letra maiúscula."),
        ResultadoCriterio(codigo="NUMEROS", descricao="Presença de pelo menos um dígito numérico", atendido=False, mensagem="A senha deve conter ao menos um dígito numérico."),
        ResultadoCriterio(codigo="ESPECIAIS", descricao="Presença de pelo menos um caractere especial", atendido=False, mensagem="A senha deve conter ao menos um caractere especial."),
        ResultadoCriterio(codigo="SEQUENCIA_SIMPLES", descricao="Ausência de sequências alfanuméricas consecutivas de 3 ou mais caracteres", atendido=False, mensagem="A senha não deve conter sequências alfanuméricas consecutivas simples (ex.: 'abc').")
        # demais critérios...
    ],
    mensagens=[
        "A senha deve ter no mínimo 8 caracteres.",
        "A senha deve conter ao menos uma letra maiúscula.",
        "A senha deve conter ao menos um dígito numérico.",
        "A senha deve conter ao menos um caractere especial.",
        "A senha não deve conter sequências alfanuméricas consecutivas simples (ex.: 'abc')."
    ]
)
```

### 5.3 Exemplo: Entrada Não String (`None`)
**Entrada:** `None`

**Retorno Python (`ResultadoValidacao`):**
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
