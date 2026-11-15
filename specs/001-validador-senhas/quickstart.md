# Guia de Início Rápido e Cenários de Validação (Quickstart)

- **Feature:** `001-validador-senhas`
- **Etapa:** E2 — Plano Técnico (`speckit-plan`)
- **Status:** CONCLUÍDO
- **Data:** 2026-11-15
- **Autor:** Arquiteto da Fábrica de Software (`subagent-arquiteto`)

---

## 1. Visão Geral e Pré-requisitos

O pacote `password_validator` oferece validação estruturada, robusta e rápida de senhas em Python.
- **Python:** Versão 3.10 ou superior (testado e homologado em Python 3.14).
- **Dependências Externas:** Nenhuma. Instalação de pacotes adicionais via `pip` é desnecessária.

---

## 2. Instalação e Estrutura de Importação

Com o diretório `src` incluído no `sys.path` (ou executando o Python a partir da raiz do projeto configurando `PYTHONPATH=src`):

```python
from password_validator import (
    validar_senha,
    eh_senha_valida,
    ResultadoValidacao,
    NivelForca,
    CodigoCriterio
)
```

---

## 3. Cenários de Uso e Exemplos Práticos

### Cenário 1: Senha Forte Aprovada (US1, US3)
Uma senha com comprimento $\ge 12$, contendo maiúsculas, minúsculas, dígitos e símbolos especiais, sem padrões triviais.

```python
resultado = validar_senha("C0mplex@Pass#2026")

print(f"Válida: {resultado.is_valid}")      # True
print(f"Força: {resultado.forca}")          # "FORTE"
print(f"Erros: {resultado.mensagens}")      # []
```

---

### Cenário 2: Senha Média Aprovada (US1, US3)
Uma senha que atende a todos os critérios obrigatórios e não contém padrões triviais, mas tem comprimento entre 8 e 11 caracteres.

```python
resultado = validar_senha("K9#mQ2$p")

print(f"Válida: {resultado.is_valid}")      # True
print(f"Força: {resultado.forca}")          # "MEDIA"
print(f"Erros: {resultado.mensagens}")      # []
```

---

### Cenário 3: Senha Curta ou com Critérios Faltantes (US1)
Uma senha com menos de 8 caracteres e ausência de maiúsculas/especiais.

```python
resultado = validar_senha("ab12")

print(f"Válida: {resultado.is_valid}")      # False
print(f"Força: {resultado.forca}")          # "FRACA"
for msg in resultado.mensagens:
    print(f"- {msg}")
# - A senha deve conter no mínimo 8 caracteres.
# - A senha deve conter ao menos uma letra maiúscula.
# - A senha deve conter ao menos um caractere especial.
```

---

### Cenário 4: Senha com Sequências Consecutivas Simples (US2)
Senhas contendo sequências óbvias de 3 ou mais caracteres como `"123"`, `"abc"`, `"321"` ou `"cba"`.

```python
resultado = validar_senha("MinhaSenha!123")

print(f"Válida: {resultado.is_valid}")      # False
print(f"Força: {resultado.forca}")          # "FRACA"
print(resultado.mensagens)
# ["A senha não deve conter sequências alfanuméricas consecutivas simples (ex.: '123', 'abc')."]
```

---

### Cenário 5: Senha com Repetições Excessivas de Caracteres (US2)
Senhas contendo 3 ou mais caracteres idênticos consecutivos (ex.: `"aaa"`, `"111"`, `"!!!"`).

```python
resultado = validar_senha("SenhaForte!!!12")

print(f"Válida: {resultado.is_valid}")      # False
print(f"Força: {resultado.forca}")          # "FRACA"
print(resultado.mensagens)
# ["A senha não deve conter 3 ou mais caracteres idênticos repetidos consecutivamente."]
```

---

### Cenário 6: Senha de Dicionário ou Termo Trivial (US2)
Senhas baseadas em termos conhecidos e vulneráveis como `"password"`, `"admin"`, `"senha123"`.

```python
resultado = validar_senha("Password123!")

print(f"Válida: {resultado.is_valid}")      # False
print(f"Força: {resultado.forca}")          # "FRACA"
print(resultado.mensagens)
# ["A senha não deve conter termos comuns, senhas conhecidas ou palavras previsíveis."]
```

---

### Cenário 7: Passphrases com Espaços Internos (US4)
Senhas em formato de frase com espaços intermediários válidos.

```python
resultado = validar_senha("Cavalo Azul Salta $123")

print(f"Válida: {resultado.is_valid}")      # True
print(f"Força: {resultado.forca}")          # "FORTE"
```

---

### Cenário 8: Resiliência contra Entradas Anômalas (`None`, não string, vazia) (US4)
Garante que a biblioteca não levanta exceções não tratadas.

```python
# Entrada None
res_none = validar_senha(None)
print(res_none.is_valid)                    # False
print(res_none.mensagens)                   # ["O valor fornecido para validação deve ser uma cadeia de texto (string)."]

# Entrada tipo Inteiro
res_int = validar_senha(12345678)
print(res_int.is_valid)                     # False
print(res_int.mensagens)                    # ["O valor fornecido para validação deve ser uma cadeia de texto (string)."]

# Entrada Vazia ou Só Espaços
res_espacos = validar_senha("     ")
print(res_espacos.is_valid)                 # False
print(res_espacos.mensagens)                # ["A senha não pode ser vazia ou composta unicamente por espaços em branco."]
```

---

## 4. Execução dos Comandos de Verificação

### 4.1 Executar os Testes Automatizados (Desenvolvedor e QA)
A partir da raiz do repositório:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

### 4.2 Executar Verificação de Sintaxe e Compilação
A partir da raiz do repositório:

```powershell
python -m compileall -q src
```
