# Fase 0: Pesquisa e Decisões Técnicas (Research)

- **Feature:** `001-validador-senhas`
- **Etapa:** E2 — Plano Técnico (`speckit-plan`)
- **Status:** CONCLUÍDO (sem pendências ou `NEEDS CLARIFICATION`)
- **Data:** 2026-11-15
- **Autor:** Arquiteto da Fábrica de Software (`subagent-arquiteto`)

---

## 1. Contexto e Objetivos de Engenharia

O motor de validação de senhas para a feature `001-validador-senhas` deve ser determinístico, thread-safe, livre de estado mutável compartilhado e altamente resiliente. O sistema deve operar de forma 100% autocontida no ecossistema da biblioteca padrão do Python (`standard library`), sem dependência de bibliotecas externas instaladas via `pip`, sem banco de dados e sem requisições de rede.

Este documento consolida as pesquisas técnicas, decisões de engenharia, alternativas avaliadas e justificativas matemáticas/algorítmicas para cada desafio técnico da especificação aprovada no Checkpoint 1.

---

## 2. Decisões Técnicas Fundamentais

### 2.1 Detecção de Sequências Alfanuméricas Simples (FR-007)

- **Requisito:** Identificar e rejeitar sequências alfabéticas ou numéricas consecutivas com 3 ou mais caracteres seguidos em ordem direta ou reversa (ex.: `"123"`, `"321"`, `"abc"`, `"cba"`, `"789"`, `"xyz"`, `"zyx"`).
- **Desafio Técnico:** A detecção deve ser insensível a maiúsculas/minúsculas, tratar dígitos e letras de forma segmentada (não misturar dígito com letra como sequência, ex.: `"9ab"` não é sequência contínua direta nos alfabetos padrão), cobrir tanto ordem ascendente (`+1`) quanto descendente (`-1`) e possuir complexidade temporal linear $O(n)$ sem explosão de expressões regulares.
- **Alternativas Avaliadas:**
  1. *Expressões Regulares Abrangentes:* Compilar listas de expressões com lookaheads ou uniões de sequências hardcoded (`123|234|345|...|abc|bcd|...`).
     - *Desvantagem:* Rígido, propenso a esquecimentos de combinações reversas, código verboso e manutenção custosa.
  2. *Janela Deslizante Aritmética sobre Pontos de Código (Unicode/ASCII):* Percorrer a string em janela deslizante de tamanho 3 ($c_0, c_1, c_2$), convertendo caracteres para minúsculo, verificando se todos pertencem à mesma categoria (`dígitos` ou `letras ASCII`) e se as diferenças consecutivas de `ord()` são estritamente iguais a `+1` (ordem direta) ou `-1` (ordem reversa).
- **Decisão Adotada:** **Janela Deslizante Aritmética**.
  - Para cada índice $i$ de $0$ até $n - 3$:
    - $c_0, c_1, c_2 = s[i], s[i+1], s[i+2]$ (normalizados em minúsculo).
    - Se $c_0, c_1, c_2$ forem todos dígitos decimais (`'0' <= c <= '9'`):
      - Se $ord(c_1) - ord(c_0) == 1$ e $ord(c_2) - ord(c_1) == 1 \implies$ **Sequência numérica direta detectada** (violação de FR-007).
      - Se $ord(c_1) - ord(c_0) == -1$ e $ord(c_2) - ord(c_1) == -1 \implies$ **Sequência numérica reversa detectada** (violação de FR-007).
    - Se $c_0, c_1, c_2$ forem todas letras ASCII (`'a' <= c <= 'z'`):
      - Se $ord(c_1) - ord(c_0) == 1$ e $ord(c_2) - ord(c_1) == 1 \implies$ **Sequência alfabética direta detectada** (violação de FR-007).
      - Se $ord(c_1) - ord(c_0) == -1$ e $ord(c_2) - ord(c_1) == -1 \implies$ **Sequência alfabética reversa detectada** (violação de FR-007).
  - *Complexidade:* $O(n)$ em tempo e $O(1)$ em espaço auxiliar. Em uma senha de 128 caracteres, a verificação executa em menos de $0.05$ ms.

---

### 2.2 Detecção de Repetições Consecutivas Idênticas (FR-008)

- **Requisito:** Identificar e rejeitar 3 ou mais caracteres idênticos consecutivos (ex.: `"aaa"`, `"111"`, `"###"`, `"   "`).
- **Desafio Técnico:** Detecção rápida em qualquer tipo de caractere (letras, dígitos, símbolos de pontuação e espaços).
- **Alternativas Avaliadas:**
  1. *Agrupamento Iterativo com `itertools.groupby`:* Agrupar caracteres adjacentes idênticos e checar se `len(list(grupo)) >= 3`.
     - *Desvantagem:* Cria listas ou contadores adicionais na memória para cada grupo.
  2. *Expressão Regular Pré-compilada com Retrovisor (Backreference):* `re.compile(r"(.)\1{2,}")`.
- **Decisão Adotada:** **Expressão Regular Pré-compilada** (`re.compile(r"(.)\1{2,}")`).
  - O motor regex do Python em C executa o backtracking de repetição em tempo extremamente reduzido ($O(n)$). Compilar a expressão no nível do módulo garante inicialização única e sem overhead em invocações subsequentes.

---

### 2.3 Detecção de Senhas Triviais e Termos de Dicionário (FR-006)

- **Requisito:** Confrontar a senha contra um catálogo imutável em memória de senhas fracas, óbvias e termos vulneráveis conhecidos (ex.: `"password"`, `"senha"`, `"admin"`, `"qwerty"`, `"123456"`, `"mudar123"`, `"senha123"`, `"admin1234"`).
- **Desafio Técnico:** A comparação deve ser insensível a maiúsculas e minúsculas. Além disso, termos triviais que formem a raiz evidente da senha combinados com sufixos triviais (como nos exemplos do Cenário 2.1: `"Password123!"`, `"admin1234@"`, `"qwerty123!"`) devem ser capturados e rejeitados.
- **Alternativas Avaliadas:**
  1. *Trie ou Aho-Corasick para busca em texto:* Estrutura avançada de árvore para busca de padrões.
     - *Desvantagem:* Complexidade excessiva para um catálogo em memória de termos triviais essenciais; violação do princípio KISS.
  2. *Conjunto Imutável (`frozenset`) com Verificação de Match Exato e Substring de Raiz:*
     - Manter um `frozenset` de termos triviais em minúsculas.
     - Avaliar se a senha inteira (em minúsculas) coincide com qualquer item do catálogo, ou se qualquer termo do catálogo (com tamanho $\ge 4$) está contido na senha.
- **Decisão Adotada:** **`frozenset` em memória com busca exata e varredura de substrings-chave**.
  - O catálogo básico conterá termos de alta prevalência: `"password"`, `"senha"`, `"admin"`, `"qwerty"`, `"123456"`, `"mudar123"`, `"senha123"`, `"admin123"`, `"admin1234"`, `"welcome"`, `"padrao"`, `"teste123"`, etc.
  - Como a consulta em `frozenset` para match exato é $O(1)$, e a varredura de substrings para uma lista concisa de dezenas de termos tem custo negligenciável em senhas de até 128 caracteres, essa abordagem atende plenamente ao critério de sucesso SC-002 (< 5 ms).

---

### 2.4 Tratamento Resiliente de Tipos e Entradas Inválidas (FR-012, US4)

- **Requisito:** Tratamento seguro e uniforme para entradas nulas (`None`), números inteiros, booleanos ou quaisquer tipos não textuais, além de entradas vazias ou exclusivamente compostas por espaços, retornando resultado estruturado sem levantar exceções não tratadas ao chamador.
- **Decisão Adotada:** **Guard Clauses Estruturadas com No-Throw Guarantee**.
  - Na entrada da função principal de validação:
    1. **Verificação de Tipo:** Se `not isinstance(senha, str)`, a função retorna imediatamente um `ResultadoValidacao` com:
       - `is_valid = False`
       - `forca = "FRACA"`
       - Critério `TIPO_ENTRADA` marcado com `atendido = False` e mensagem: `"O valor fornecido para validação deve ser uma cadeia de texto (string)."`
       - Lista consolidada `mensagens = ["O valor fornecido para validação deve ser uma cadeia de texto (string)."]`
    2. **Verificação de String Vazia ou Só Espaços:** Se `len(senha.strip()) == 0`, a função retorna imediatamente um `ResultadoValidacao` com:
       - `is_valid = False`
       - `forca = "FRACA"`
       - Critério `NAO_VAZIA` marcado com `atendido = False` e mensagem: `"A senha não pode ser vazia ou composta unicamente por espaços em branco."`
       - Lista consolidada `mensagens = ["A senha não pode ser vazia ou composta unicamente por espaços em branco."]`
  - Dessa forma, nenhuma exceção (`TypeError`, `AttributeError`, `ValueError`) vaza para o integrador.

---

### 2.5 Regras Estruturais e Suporte a Passphrases e Unicode (FR-001 a FR-005, FR-011)

- **Comprimento Mínimo (FR-001):** `len(senha) >= 8`.
- **Preservação de Espaços Internos (FR-011):** Espaços intermediários em frases secretas (passphrases) são preservados na contagem de caracteres (`len(senha)` usa a string original completa, sem `.strip()`).
- **Letras Minúsculas (FR-002) e Maiúsculas (FR-003):** Utilização de `any(c.islower() for c in senha)` e `any(c.isupper() for c in senha)`. No Python 3, os métodos `islower()` e `isupper()` oferecem suporte nativo total ao padrão Unicode (ex.: `"ç"`, `"ã"`, `"é"` são reconhecidos como minúsculos; `"Ç"`, `"Ã"` como maiúsculos), atendendo diretamente ao Cenário 4.4 de US4.
- **Dígitos Numéricos (FR-004):** `any(c.isdigit() for c in senha)`.
- **Caracteres Especiais (FR-005):** Caracteres que não são alfanuméricos e não são espaços em branco. Definido via conjunto padrão ou expressão `re.search(r"[^\w\s]|_", senha)` ou `any(c in string.punctuation or (not c.isalnum() and not c.isspace()) for c in senha)`.

---

### 2.6 Algoritmo de Avaliação e Classificação de Força (FR-009, US3)

- **Regras de Negócio Estabelecidas na Spec:**
  - Classificação no campo `forca`:
    - `"FRACA"`: Se `is_valid is False` (ou seja, descumpriu qualquer critério estrutural obrigatório ou violou regras de segurança como senhas triviais, sequências simples ou repetições).
    - `"MEDIA"`: Se `is_valid is True` (todos os critérios obrigatórios e regras de segurança foram cumpridos), porém o comprimento da senha está entre 8 e 11 caracteres (`8 <= len(senha) < 12`).
    - `"FORTE"`: Se `is_valid is True` (todos os critérios obrigatórios e regras de segurança foram cumpridos), o comprimento é igual ou superior a 12 caracteres (`len(senha) >= 12`) e há ampla diversidade de caracteres (presença de maiúsculas, minúsculas, dígitos e especiais).

---

### 2.7 Estratégia de Testes e Execução Automática (SC-001, SC-004)

- **Framework de Testes:** Módulo nativo `unittest` da standard library do Python.
- **Comando de Teste:** `python -m unittest discover -s tests -p "test_*.py"`
- **Verificação de Sintaxe/Compilação:** `python -m compileall -q src`
- **Separação de Testes:**
  - `tests/unit/`: Testes unitários de responsabilidade do Desenvolvedor em E4.
  - `tests/integration/`: Testes de integração/aceite e cenários ponta a ponta avaliados pelo Analista de QA em E6.

---

## 3. Alternativas Técnicas Avaliadas e Matriz de Decisão

| Tópico | Alternativa A (Rejeitada) | Alternativa B (Adotada) | Justificativa da Escolha |
|---|---|---|---|
| **Dependências Externas** | Usar bibliotecas `pydantic`, `pytest`, `zxcvbn` | Usar Python Standard Library (`dataclasses`, `enum`, `re`, `unittest`) | Conformidade estrita com SC-001 e Princípio 1.3 da Constituição (Simplicidade / Zero dependências externas). |
| **Detecção de Sequências** | Expressão Regular Complexa com lookaheads | Janela Deslizante Aritmética ($ord(c_{i+1}) - ord(c_i)$) | Manutenibilidade superior, cobre ordens diretas e reversas sem falsos negativos em números e letras, $O(n)$ garantido. |
| **Modelagem de Dados** | Dicionários Python puros (`dict`) | `@dataclass(frozen=True)` com tipagem estrita | Tipagem estática, autocompletação em IDEs, imutabilidade thread-safe e exportação direta para `dict`. |
| **Tratamento de Exceções** | Lançar `TypeError` ou `ValueError` para entradas inválidas | Retornar `ResultadoValidacao(is_valid=False, forca="FRACA")` | Requisito explícito de resiliência (FR-012 e US4), evitando travamentos na aplicação chamadora. |

---

## 4. Análise de Desempenho e Complexidade Computacional

- **Complexidade Temporal:** $O(n)$ onde $n$ é o comprimento da senha. Como a especificação prevê validações típicas de até 128 caracteres, todas as verificações executam em menos de $1$ ms, superando com folga a meta de SC-002 (< 5 ms).
- **Complexidade Espacial:** $O(1)$ espaço auxiliar adicional, pois não há alocação de estruturas de tamanho dinâmico proporcional a grandes coleções.
- **Concorrência e Thread-Safety:** Todas as funções são puras (side-effect free) e os catálogos de termos são constantes imutáveis (`frozenset`). Nenhuma variável mutável de escopo global é compartilhada.
