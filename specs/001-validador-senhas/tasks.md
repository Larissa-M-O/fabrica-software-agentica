# Plano de Tarefas de Implementação: Validador de Senhas

- **Feature:** `001-validador-senhas`
- **Branch:** `001-validador-senhas`
- **Etapa:** E3 — Criação de Tarefas (`speckit-tasks`)
- **Status:** PENDENTE
- **Data de Criação:** 2026-11-15
- **Rastreabilidade da Especificação:** [spec.md](spec.md) (Aprovada no Checkpoint 1)
- **Rastreabilidade do Plano Técnico:** [plan.md](plan.md) (Validado em E2)
- **Rastreabilidade do Modelo de Dados:** [data-model.md](data-model.md)
- **Rastreabilidade dos Contratos:** [contracts/validator_api.md](contracts/validator_api.md)

---

## 1. Visão Geral e Estratégia de Implementação

### 1.1 Estratégia de Entrega Incremental e MVP
A implementação é estruturada em 7 fases sequenciais de entrega, permitindo validação contínua da menor fatia funcional viável até o produto completo:
- **MVP (Mínimo Produto Viável):** Composto pelas Fases 1 (Setup), 2 (Foundational) e 3 (US1 — Complexidade Estrutural). Entrega a capacidade fundamental de validação de tamanho mínimo, maiúsculas, minúsculas, números e caracteres especiais em `rules.py`.
- **Incremento 2 (Segurança Avançada):** Fase 4 (US2 — Senhas Triviais e Padrões Simples). Adiciona detecção de termos de dicionário, sequências alfanuméricas e repetições consecutivas.
- **Incremento 3 (Motor Consolidado e Contratos Públicos):** Fase 5 (US3 — Apresentação Estruturada e Cálculo de Força). Implementa o orquestrador principal em `validator.py`, cálculo de `forca` (`FRACA`, `MEDIA`, `FORTE`) e emissão do contrato unificado `ResultadoValidacao`.
- **Incremento 4 (Resiliência e Tolerância a Falhas):** Fase 6 (US4 — Resiliência de Entradas e Casos de Borda). Garante a política *no-throw guarantee* para `None` e tipos não string, preservação de espaços em passphrases e suporte a caracteres acentuados Unicode.
- **Incremento 5 (Polimento e Documentação):** Fase 7 (Polish). Configura a API pública no pacote `__init__.py`, documenta o uso em `README.md` e executa a verificação final de conformidade.

### 1.2 Regras de Paralelismo `[P]`
- Tarefas marcadas com `[P]` atuam em arquivos independentes e não possuem dependências bloqueantes diretas em relação a outras tarefas da mesma fase.
- Tarefas sem `[P]` devem ser executadas em sequência estrita, pois modificam o mesmo módulo ou dependem de artefatos produzidos na tarefa imediatamente anterior.

### 1.3 Comandos de Verificação Mandatórios (`state.json.commands`)
A cada fase de implementação, o Desenvolvedor deve assegurar que todos os testes passem com código de saída 0:
- **Testes Unitários:** `python -m unittest discover -s tests -p "test_*.py"`
- **Verificação Sintática e Compilação:** `python -m compileall -q src`

---

## 2. Dependências entre Fases

```
┌────────────────────────────────────────────────────────┐
│ Fase 1: Setup (Estrutura de Diretórios e Pacotes)      │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Fase 2: Foundational (Models, Enums e Catálogo)        │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Fase 3: US1 [P1] (Validação Estrutural de Complexidade)│
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Fase 4: US2 [P1] (Rejeição de Triviais e Padrões)      │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Fase 5: US3 [P2] (Apresentação Estruturada e Força)    │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Fase 6: US4 [P3] (Resiliência e Casos de Borda)        │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Fase 7: Polish (API Pública, Documentação e Validação) │
└────────────────────────────────────────────────────────┘
```

---

## 3. Fases de Execução e Tarefas Detalhadas

### Fase 1 — Setup (Preparação do Ambiente e Estrutura)
- **Objetivo:** Estabelecer a árvore física de diretórios do código-fonte e dos testes unitários, garantindo isolamento modular conforme o plano de arquitetura.
- **Dependências:** Nenhuma.

- [X] T001 [P] Criar a estrutura do diretório do pacote de código-fonte em `src/password_validator/` e inicializar o arquivo vazio `src/password_validator/__init__.py`.
- [X] T002 [P] Criar a estrutura de diretórios para testes unitários em `tests/unit/` e inicializar o arquivo vazio `tests/__init__.py` e `tests/unit/__init__.py`.

---

### Fase 2 — Foundational (Entidades Básicas e Catálogo de Domínio)
- **Objetivo:** Implementar as estruturas de dados imutáveis, enumerações de domínio e catálogo em memória de termos triviais definidos em `data-model.md`.
- **Dependências:** Fase 1 (Setup concluído).

- [X] T003 [P] Implementar as enumerações `NivelForca` (`FRACA`, `MEDIA`, `FORTE`), `CodigoCriterio` e as dataclasses imutáveis `ResultadoCriterio` e `ResultadoValidacao` com seus respectivos métodos `to_dict()` em `src/password_validator/models.py`.
- [X] T004 Implementar a suíte de testes unitários para validação de imutabilidade, conversão para dicionário e invariantes dos modelos em `tests/unit/test_models.py`.
- [X] T005 [P] Implementar o catálogo imutável em memória de senhas triviais e termos vulneráveis (`frozenset` insensível a maiúsculas/minúsculas) em `src/password_validator/trivial_passwords.py`.

---

### Fase 3 — US1 [P1] — Validação de Requisitos Estruturais de Complexidade
- **Objetivo da História:** Validar se a senha cumpre as regras estruturais obrigatórias de comprimento mínimo de 8 caracteres, presença de letras maiúsculas, minúsculas, números e caracteres especiais.
- **Teste Independente:** Executar `python -m unittest tests/unit/test_rules.py` confirmando a aprovação e reprovação precisa de cada regra estrutural isolada (`FR-001` a `FR-005`).
- **Dependências:** Fase 2 (Models disponíveis).

- [X] T006 [US1] Implementar as funções avaliadoras de regras estruturais `validar_tamanho_minimo`, `validar_maiusculas`, `validar_minusculas`, `validar_numeros` e `validar_especiais` retornando objetos `ResultadoCriterio` em `src/password_validator/rules.py`.
- [X] T007 [US1] Implementar os testes unitários cobrindo todos os cenários da história US1 (cenários 1.1 a 1.6: comprimento mínimo, maiúsculas, minúsculas, números e especiais) para `rules.py` em `tests/unit/test_rules.py`.

---

### Fase 4 — US2 [P1] — Identificação e Rejeição de Senhas Triviais e Padrões Simples
- **Objetivo da História:** Rejeitar senhas baseadas em termos conhecidos/dicionário em memória, sequências alfanuméricas consecutivas (3+ caracteres diretos ou reversos) e repetições consecutivas idênticas (3+ caracteres).
- **Teste Independente:** Executar `python -m unittest tests/unit/test_rules.py` validando os casos de termos triviais, sequências e repetições (`FR-006` a `FR-008`).
- **Dependências:** Fase 2 (Catálogo em memória) e Fase 3 (Módulo `rules.py` inicializado).

- [X] T008 [US2] Implementar a regra de detecção de senhas triviais e de dicionário `validar_senha_trivial` confrontando a senha contra o catálogo `trivial_passwords.py` de forma insensível a maiúsculas/minúsculas em `src/password_validator/rules.py`.
- [X] T009 [US2] Implementar a regra de detecção de sequências alfanuméricas simples diretas e reversas de 3 ou mais caracteres `validar_sequencia_simples` com algoritmo de janela deslizante em `src/password_validator/rules.py`.
- [X] T010 [US2] Implementar a regra de detecção de repetições de 3 ou mais caracteres idênticos consecutivos `validar_repeticao_caracteres` em `src/password_validator/rules.py`.
- [X] T011 [US2] Incrementar a suíte de testes unitários com os cenários da história US2 (cenários 2.1 a 2.4: detecção de dicionário, sequências diretas/reversas e repetições de caracteres) em `tests/unit/test_rules.py`.

---

### Fase 5 — US3 [P2] — Apresentação do Resultado Estruturado e Cálculo de Força
- **Objetivo da História:** Orquestrar a execução de todas as regras, calcular o nível de força da senha (`FRACA`, `MEDIA`, `FORTE`) e emitir o diagnóstico completo e unificado no objeto `ResultadoValidacao` com os campos `is_valid`, `forca`, `criterios` e `mensagens`.
- **Teste Independente:** Executar `python -m unittest tests/unit/test_validator.py` validando a classificação de força e o contrato de saída estruturado em conformidade com `contracts/validator_api.md` (`FR-009`, `FR-010`).
- **Dependências:** Fase 3 e Fase 4 (Todas as regras de avaliação disponíveis).

- [X] T012 [US3] Implementar o algoritmo determinístico de pontuação e classificação de força `calcular_forca` retornando `NivelForca.FRACA`, `NivelForca.MEDIA` ou `NivelForca.FORTE` em `src/password_validator/validator.py`.
- [X] T013 [US3] Implementar as funções públicas `validar_senha` e `eh_senha_valida` orquestrando os critérios de `rules.py`, agregando as mensagens corretivas em linguagem natural (pt-BR) e construindo o objeto `ResultadoValidacao` em `src/password_validator/validator.py`.
- [X] T014 [US3] Implementar a suíte de testes unitários cobrindo todos os cenários da história US3 (cenários 3.1 a 3.3: classificação de força, lista consolidada de mensagens e função helper booleana) em `tests/unit/test_validator.py`.

---

### Fase 6 — US4 [P3] — Resiliência de Entradas e Casos de Borda
- **Objetivo da História:** Garantir que o validador lide com segurança com entradas `None`, tipos incompatíveis (inteiros, booleanos, dicionários), strings vazias, strings com apenas espaços, passphrases com espaços intermediários e caracteres acentuados/Unicode sem levantar exceções (*no-throw guarantee*).
- **Teste Independente:** Executar `python -m unittest tests/unit/test_validator.py` cobrindo cenários com `None`, tipos não string, passphrases e Unicode (`FR-011`, `FR-012`).
- **Dependências:** Fase 5 (Módulo `validator.py` orquestrador implementado).

- [X] T015 [US4] Implementar guard clauses para tratamento resiliente de entradas `None`, tipos não string (`isinstance(senha, str)` retornando `is_valid=False`, `forca="FRACA"` e mensagem orientativa) e entradas vazias ou contendo apenas espaços em `src/password_validator/validator.py`.
- [X] T016 [US4] Assegurar o suporte a passphrases (preservação de espaços internos para contagem de comprimento) e validação compatível com caracteres acentuados e símbolos Unicode em `src/password_validator/validator.py`.
- [X] T017 [US4] Implementar a suíte de testes unitários cobrindo todos os cenários da história US4 (cenários 4.1 a 4.4: None, tipos numéricos/booleanos, string vazia, apenas espaços, passphrases e Unicode) em `tests/unit/test_validator.py`.

---

### Fase 7 — Polish (Polimento, Exportações da API e Validação Final)
- **Objetivo da Fase:** Expor a interface pública no pacote principal, documentar instruções de uso e certificar que todos os comandos de validação executam perfeitamente com código de saída 0.
- **Dependências:** Fases 1 a 6 concluídas.

- [ ] T018 [P] Configurar as exportações da API pública (`validar_senha`, `eh_senha_valida`, `ResultadoValidacao`, `ResultadoCriterio`, `NivelForca`, `CodigoCriterio`) com `__all__` em `src/password_validator/__init__.py`.
- [ ] T019 [P] Documentar instruções de instalação, exemplos de importação e cenários práticos de uso no arquivo de documentação `README.md`.
- [ ] T020 Executar a verificação integral da sintaxe do pacote via `python -m compileall -q src` e a suíte completa de testes unitários via `python -m unittest discover -s tests -p "test_*.py"`, garantindo código de saída 0.

---

## 4. Matriz de Rastreabilidade Plan-to-Task e Cobertura de Requisitos

| Requisito Funcional | Descrição | História | Tarefas de Implementação e Teste | Status de Cobertura |
|---|---|---|---|:---:|
| **FR-001** | Comprimento mínimo de 8 caracteres | US1, US3 | `T006`, `T007` | **COBERTO** |
| **FR-002** | Validação de letras minúsculas | US1, US3 | `T006`, `T007` | **COBERTO** |
| **FR-003** | Validação de letras maiúsculas | US1, US3 | `T006`, `T007` | **COBERTO** |
| **FR-004** | Validação de dígitos numéricos | US1, US3 | `T006`, `T007` | **COBERTO** |
| **FR-005** | Validação de caracteres especiais | US1, US3 | `T006`, `T007` | **COBERTO** |
| **FR-006** | Detecção de senhas triviais e de dicionário | US2, US3 | `T005`, `T008`, `T011` | **COBERTO** |
| **FR-007** | Detecção de sequências alfanuméricas simples (3+ chars) | US2, US3 | `T009`, `T011` | **COBERTO** |
| **FR-008** | Detecção de repetições consecutivas idênticas (3+ chars) | US2, US3 | `T010`, `T011` | **COBERTO** |
| **FR-009** | Classificação de força da senha (`FRACA`, `MEDIA`, `FORTE`) | US3 | `T012`, `T014` | **COBERTO** |
| **FR-010** | Relatório estruturado de validação (`ResultadoValidacao`) | US3 | `T003`, `T013`, `T014` | **COBERTO** |
| **FR-011** | Suporte a passphrases e espaços internos | US4 | `T016`, `T017` | **COBERTO** |
| **FR-012** | Tratamento seguro de tipos e entradas anômalas (*No-Throw*) | US4 | `T015`, `T017` | **COBERTO** |

### Critérios de Sucesso (Não Funcionais):
- **SC-001 (Zero Dependências Externas):** Coberto em todas as tarefas (100% Python Standard Library).
- **SC-002 (Desempenho < 5ms):** Coberto pelas implementações eficientes $O(n)$ em `T006`, `T009`, `T010`, `T012`.
- **SC-003 (Determinismo e Imutabilidade):** Coberto por `T003` (`frozen=True`), `T005` (`frozenset`) e `T013`.
- **SC-004 (Cobertura Completa de Testes):** Coberto por `T004`, `T007`, `T011`, `T014`, `T017` e `T020`.
- **SC-005 (Mensagens Claras em pt-BR):** Coberto pelas mensagens padronizadas em `T006`, `T008`, `T009`, `T010`, `T013`, `T015`.

---

## 5. Exemplos de Execução Paralela

Durante a execução da etapa E4 pelo Desenvolvedor, os seguintes pares ou grupos de tarefas podem ser trabalhados ou analisados de forma paralela/independente:

1. **Fase 1 (Setup):**
   - `T001` (`src/password_validator/`) e `T002` (`tests/unit/`) são independentes entre si.
2. **Fase 2 (Foundational):**
   - `T003` (`models.py`) e `T005` (`trivial_passwords.py`) operam em módulos isolados sem dependências cruzadas.
3. **Fase 7 (Polish):**
   - `T018` (`src/password_validator/__init__.py`) e `T019` (`README.md`) atuam em arquivos completamente distintos.
