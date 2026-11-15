# Plano Técnico de Implementação: Validador de Senhas

- **Feature:** `001-validador-senhas`
- **Etapa:** E2 — Plano Técnico (`speckit-plan`)
- **Status:** CONCLUÍDO
- **Data:** 2026-11-15
- **Branch da Feature:** `001-validador-senhas`
- **Validação Checkpoint 1:** Ratificada pelo humano ("Aprovado")
- **Autor:** Arquiteto da Fábrica de Software (`subagent-arquiteto`)

---

## 1. Resumo Executivo e Abordagem Técnica

O objetivo deste plano é estruturar a implementação da feature `001-validador-senhas` em um motor modular, determinístico e extensível em Python puro (Standard Library), em estrita conformidade com a especificação aprovada no Checkpoint 1 e com a Constituição da Fábrica de Software.

### Principais Pilares da Abordagem:
1. **Zero Dependências Externas (SC-001):** Utilização exclusiva da biblioteca padrão do Python (`dataclasses`, `enum`, `re`, `typing`, `unittest`, `string`). Nenhuma dependência externa via `pip`, sem banco de dados e sem chamadas de rede.
2. **Separação Limpa de Responsabilidades (Princípio SOLID/KISS):**
   - `models.py`: Entidades e enumerações imutáveis (`ResultadoValidacao`, `ResultadoCriterio`, `NivelForca`, `CodigoCriterio`).
   - `trivial_passwords.py`: Catálogo imutável em memória de termos triviais e vulneráveis.
   - `rules.py`: Funções puras de avaliação para cada critério individual (tamanho, caracteres, sequências, repetições).
   - `validator.py`: Orquestrador da validação, guard clauses de tipo e cálculo de força consolidada.
3. **Resiliência e Tolerância a Falhas (*No-Throw Guarantee*, FR-012, US4):** Entradas `None` e tipos não string não propagam exceções não tratadas; retornam imediatamente um `ResultadoValidacao` com `is_valid = False`, `forca = "FRACA"` e mensagem orientando que o dado de entrada deve ser uma string.
4. **Desempenho de Alta Eficiência (SC-002):** Processamento em tempo linear $O(n)$ com janela deslizante para sequências e regex pré-compilada para repetições, garantindo tempo de resposta $< 1$ ms para senhas de até 128 caracteres.

---

## 2. Contexto Técnico e Comandos de Verificação

Os comandos a seguir são declarados formalmente para inclusão em `specs/001-validador-senhas/state.json` pelo Orquestrador Central e governam os critérios de avanço das etapas subsequentes (E4, E5, E6, E7):

### 2.1 Comandos do Projeto (`state.json.commands`)
- **Teste (obrigatório):**
  ```powershell
  python -m unittest discover -s tests -p "test_*.py"
  ```
- **Lint / Typecheck (verificação de integridade e sintaxe):**
  ```powershell
  python -m compileall -q src
  ```
- **Build:** `null` (linguagem interpretada em Python puro sem etapa de empacotamento binário).

### 2.2 Estrutura de Diretórios de Testes
- **Testes Unitários (Desenvolvedor em E4):** `tests/unit/`
  - Focado no teste isolado de modelos, regras individuais e do validador.
- **Testes de Integração e Aceite (Analista de QA em E6):** `tests/integration/`
  - Focado em cenários ponta a ponta, compatibilidade com contratos, passphrases, caracteres Unicode e casos de borda.

---

## 3. Constitution Check (Avaliação de Conformidade Constitucional)

| Artigo da Constituição | Requisito Constitucional | Análise de Conformidade do Plano | Status |
|---|---|---|:---:|
| **Art. 1 — Princípios de Arquitetura** | Hub-and-Spoke, KISS, DRY, SOLID, diretriz de raiz limpa, isolamento de diretórios em `specs/<feature>/`. | Arquitetura simples e coesa em `src/password_validator/`. Zero arquivos de controle na raiz. Todos os artefatos de planejamento restritos a `specs/001-validador-senhas/`. | **APROVADO** |
| **Art. 2 — Qualidade e Legibilidade** | Responsabilidade única, tipagem estrita, código limpo, tratamento explícito e seguro de exceções. | Módulos pequenos e coesos (`models`, `rules`, `validator`). Tipagem completa com `dataclasses` e `typing`. *No-throw guarantee* para resiliência de integradores. | **APROVADO** |
| **Art. 3 — Testes e DoD** | DoD com testes automatizados, comandos declarados com código de saída 0, testes em terminal real. | Comandos declarados (`unittest`). Suíte unitária em `tests/unit/` e integração em `tests/integration/`. Sem dependência de runners externos. | **APROVADO** |
| **Art. 4 — Segurança e Proteção** | Sem segredos versionados, validação e sanitização de dados, ausência de vulnerabilidades de injeção. | Validador puro em memória. Não manipula credenciais reais, sem persistência em disco ou banco, imutabilidade garantida. | **APROVADO** |
| **Art. 5 — Rastreabilidade** | Identificadores `FR-xxx`, `SC-xxx`, `USn`, rastreabilidade plan-to-task e cobertura completa de requisitos. | Todos os 12 requisitos (`FR-001` a `FR-012`), 5 critérios de sucesso (`SC-001` a `SC-005`) e 4 histórias mapeados para módulos e testes. | **APROVADO** |
| **Art. 6 — Revisão de Código** | Severidades padronizadas, sem alterações de código pelo revisor. | Arquitetura compatível com revisão incremental por arquivos (`models.py` → `rules.py` → `validator.py`). | **APROVADO** |
| **Art. 7 — Governança dos Subagentes** | Contexto isolado, sem subagente acionar subagente, retorno em bloco padronizado STATUS. | O Arquiteto opera exclusivamente em E2, sem delegar a outros subagentes e com retorno padronizado ao Orquestrador. | **APROVADO** |
| **Art. 8 — Controle Humano** | Respeito estrito aos Checkpoints 1 e 2. Validação textual de aprovação prévia. | Validação prévia confirmada com aprovação literal do humano no Checkpoint 1 ("Aprovado"). Parada para Checkpoint 2 preservada. | **APROVADO** |
| **Art. 9 — Proteção de Git e Entrega** | Operação na branch da feature (`001-validador-senhas`), proibição de ações destrutivas ou commits por subagentes. | Trabalho validado na branch `001-validador-senhas`. Subagente não realiza commits nem comandos de CLI `gh`. | **APROVADO** |

---

## 4. Complexity Tracking (Rastreamento de Complexidade)

- **Complexidade Acidental:** Nenhuma. O projeto foi projetado com a máxima simplicidade e aderência ao princípio KISS.
- **Dependências Externas:** 0 dependências. A solução usa 100% da biblioteca padrão do Python.
- **Banco de Dados / Armazenamento:** Não aplicável (catálogo de termos fracos gerenciado em `frozenset` em memória).
- **Rede / Comunicações Externas:** Não aplicável.
- **Violações Constitucionais Justificadas:** Nenhuma violação detectada. O projeto atende com rigor a todas as disposições da Constituição.

---

## 5. Estrutura do Projeto e Módulos Previstos

A implementação será organizada na seguinte árvore de arquivos e diretórios:

```text
fabrica-software-agentica-main/
├── src/
│   └── password_validator/
│       ├── __init__.py               # Exporta funções públicas e modelos do pacote
│       ├── models.py                 # Dataclasses imutáveis e Enums (ResultadoValidacao, etc.)
│       ├── trivial_passwords.py      # Catálogo em frozenset de termos e senhas comuns
│       ├── rules.py                  # Funções avaliadoras de critérios individuais
│       └── validator.py              # Motor principal de validação e guard clauses
├── tests/
│   ├── __init__.py                   # Pacote de testes
│   ├── unit/                         # Testes Unitários (Desenvolvedor em E4)
│   │   ├── __init__.py
│   │   ├── test_models.py            # Validação estrutural de tipos, imutabilidade e to_dict
│   │   ├── test_rules.py             # Testes granulares de cada regra de rules.py
│   │   └── test_validator.py         # Teste do fluxo do validador e guard clauses
│   └── integration/                  # Testes de Aceite e E2E (QA em E6)
│       ├── __init__.py
│       └── test_e2e_scenarios.py     # Validação de cenários US1, US2, US3, US4 e casos de borda
└── specs/
    └── 001-validador-senhas/
        ├── checklists/
        │   └── requirements.md       # Checklist validado em E1
        ├── contracts/
        │   └── validator_api.md      # Contrato de interface pública gerado em E2
        ├── data-model.md             # Modelagem de dados detalhada gerada em E2
        ├── plan.md                   # Este plano técnico de implementação (E2)
        ├── quickstart.md             # Guia rápido de uso gerado em E2
        ├── research.md               # Pesquisa técnica e alternativas geradas em E2
        ├── spec.md                   # Especificação de requisitos aprovada no Checkpoint 1
        └── state.json                # Estado auditável do fluxo gerenciado pelo Orquestrador
```

---

## 6. Mapeamento de Requisitos e Rastreabilidade Bidirecional

| Requisito | Descrição | Histórias Vinculadas | Módulo Implementador | Arquivo de Teste Associado |
|---|---|---|---|---|
| **FR-001** | Comprimento mínimo de 8 caracteres | US1, US3 | `src/password_validator/rules.py` | `tests/unit/test_rules.py`, `tests/integration/test_e2e_scenarios.py` |
| **FR-002** | Validação de letras minúsculas | US1, US3 | `src/password_validator/rules.py` | `tests/unit/test_rules.py`, `tests/integration/test_e2e_scenarios.py` |
| **FR-003** | Validação de letras maiúsculas | US1, US3 | `src/password_validator/rules.py` | `tests/unit/test_rules.py`, `tests/integration/test_e2e_scenarios.py` |
| **FR-004** | Validação de dígitos numéricos | US1, US3 | `src/password_validator/rules.py` | `tests/unit/test_rules.py`, `tests/integration/test_e2e_scenarios.py` |
| **FR-005** | Validação de caracteres especiais | US1, US3 | `src/password_validator/rules.py` | `tests/unit/test_rules.py`, `tests/integration/test_e2e_scenarios.py` |
| **FR-006** | Detecção de senhas triviais e dicionário | US2, US3 | `src/password_validator/trivial_passwords.py`, `rules.py` | `tests/unit/test_rules.py`, `tests/integration/test_e2e_scenarios.py` |
| **FR-007** | Detecção de sequências alfanuméricas simples | US2, US3 | `src/password_validator/rules.py` | `tests/unit/test_rules.py`, `tests/integration/test_e2e_scenarios.py` |
| **FR-008** | Detecção de repetições consecutivas idênticas | US2, US3 | `src/password_validator/rules.py` | `tests/unit/test_rules.py`, `tests/integration/test_e2e_scenarios.py` |
| **FR-009** | Classificação de força da senha (`FRACA`, `MEDIA`, `FORTE`) | US3 | `src/password_validator/validator.py` | `tests/unit/test_validator.py`, `tests/integration/test_e2e_scenarios.py` |
| **FR-010** | Relatório estruturado de validação (`ResultadoValidacao`) | US3 | `src/password_validator/models.py`, `validator.py` | `tests/unit/test_models.py`, `tests/unit/test_validator.py` |
| **FR-011** | Suporte a passphrases e espaços internos | US4 | `src/password_validator/validator.py`, `rules.py` | `tests/unit/test_validator.py`, `tests/integration/test_e2e_scenarios.py` |
| **FR-012** | Tratamento seguro de tipos e entradas anômalas | US4 | `src/password_validator/validator.py` | `tests/unit/test_validator.py`, `tests/integration/test_e2e_scenarios.py` |

---

## 7. Estratégia de Configuração e Gestão de Segredos

- **Variáveis Sensíveis:** Inexistentes. O motor de validação não manipula credenciais persistentes, tokens, senhas reais ou conexões de rede.
- **Configurações de Teste:** O módulo opera exclusivamente com dados sintetizados e passados diretamente em memória nos casos de teste de `tests/`.
- **Compatibilidade de Ambiente:** Não requer criação de arquivo `.env` para o funcionamento do motor de senhas. A notificação via Slack (se utilizada) permanece restrita à governança do Orquestrador via variável de ambiente `$env:SLACK_WEBHOOK_URL`.

---

## 8. Avaliação de Riscos e Mitigações

1. **Risco:** Incompatibilidade com senhas contendo caracteres especiais acentuados ou símbolos Unicode raros.
   - *Mitigação:* As verificações alfabéticas de maiúsculas/minúsculas utilizam `c.isupper()` e `c.islower()` nativos do Python 3, que cobrem nativamente o espectro Unicode (ex.: `"ã"`, `"ç"`, `"é"`).
2. **Risco:** Falsos positivos na identificação de sequências consecutivas (ex.: tratar transição de dígito para letra como sequência contínua).
   - *Mitigação:* O algoritmo de janela deslizante verifica estritamente que os 3 caracteres pertençam à mesma classe (todos dígitos ou todas letras ASCII), garantindo isolamento total.
3. **Risco:** Lançamento acidental de exceção ao receber objetos exóticos de integradores (ex.: geradores, dicionários, objetos customizados).
   - *Mitigação:* A guard clause inicial avalia `isinstance(senha, str)` antes de qualquer acesso a métodos ou propriedades do objeto, retornando imediatamente um objeto estruturado inválido.

---

## 9. Próximos Passos no Ciclo de Vida

Com a conclusão e aprovação desta etapa de planejamento (E2):
1. O Orquestrador registrará os comandos em `state.json.commands`:
   - `test`: `"python -m unittest discover -s tests -p \"test_*.py\""`
   - `lint`: `"python -m compileall -q src"`
   - `build`: `null`
2. O Orquestrador acionará o Criador de Tarefas (`subagent-criador-tarefas`) para a etapa **E3 — Criação de Tarefas (`speckit-tasks`)**, gerando `specs/001-validador-senhas/tasks.md` dividido em fases incrementais com marcadores canônicos (`T001`, `[P]`, `[USn]`).
