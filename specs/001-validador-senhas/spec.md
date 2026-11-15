# Especificação de Requisitos: Validador de Senhas

- **Feature:** `001-validador-senhas`
- **Etapa:** E1 — Especificação de Requisitos (Revisão Checkpoint 1)
- **Status:** HUMAN_REVIEW_REQUIRED
- **Data de Atualização:** 2026-11-15
- **Rastreabilidade da Constituição:** Em conformidade estrita com [.specify/memory/constitution.md](../../.specify/memory/constitution.md)

---

## 1. Visão Geral e Contexto

O objetivo desta funcionalidade é fornecer um motor de validação de senhas robusto, determinístico e extensível desenvolvido em Python puro (utilizando exclusivamente a biblioteca padrão), sem dependência de bancos de dados ou serviços externos (APIs).

O validador é responsável por inspecionar senhas fornecidas pelo usuário ou sistemas chamadores, avaliando requisitos estruturais de complexidade (tamanho, variação de caracteres), identificando padrões fracos ou triviais (senhas comuns, sequências e repetições) e emitindo um diagnóstico detalhado, amigável e estruturado sobre a conformidade e a força da senha analisada.

### 1.1 Atores do Sistema
- **Sistema Integrador / Aplicação Chamadora:** Módulo ou camada da aplicação que invoca a validação de senha passando uma sequência de caracteres e recebendo o resultado estruturado.
- **Usuário Final:** Pessoa que cadastra ou altera sua senha e precisa de orientações claras e acionáveis caso a senha não atenda aos padrões exigidos.

---

## 2. Esclarecimentos e Decisões de Especificação (`## Clarifications`)

### Sessão 1 — Consolidação da Demanda Inicial
- **Pergunta 1:** Qual deve ser o tamanho mínimo aceito por padrão para senhas válidas?
  - **Decisão/Resposta:** O tamanho mínimo padrão é de **8 caracteres**, alinhado com as diretrizes de segurança da indústria (OWASP e NIST SP 800-63B).
- **Pergunta 2:** O que caracteriza "caracteres especiais"?
  - **Decisão/Resposta:** Consideram-se caracteres especiais quaisquer símbolos gráficos de pontuação e caracteres não alfanuméricos padrão (ex.: `!@#$%^&*()-_=+[]{}|;:,.<>?/~`).
- **Pergunta 3:** Quais critérios definem senhas triviais e sequências simples?
  - **Decisão/Resposta:**
    1. Presença de termos comuns de uma lista padrão em memória (ex.: "password", "senha123", "admin", "qwerty", "123456", insensível a maiúsculas/minúsculas).
    2. Sequências alfanuméricas consecutivas de 3 ou mais caracteres (ex.: "123", "abc", "cba", "321").
    3. Repetições consecutivas idênticas de 3 ou mais caracteres (ex.: "aaa", "111", "!!!").
- **Pergunta 4:** O validador deve permitir espaços na senha?
  - **Decisão/Resposta:** Sim. Espaços internos (como em passphrases) são permitidos e contam como caracteres válidos. No entanto, senhas compostas exclusivamente por espaços em branco são tratadas como vazias/inválidas.

### Sessão 2 — Ajustes do Checkpoint 1 (Padronização e Tratamento de Entradas Inválidas)
- **Foco da rodada:** Solicitação do humano no Checkpoint 1 para padronização rigorosa dos nomes dos campos do resultado e unificação do comportamento para valores `None` e tipos não string.
- **Ponto 1 (Padronização do retorno):** Como nomear os campos de força e mensagens descritivas do resultado de validação de forma unificada em todos os pontos da especificação?
  - **Decisão/Resposta:** Os campos foram estritamente unificados como `forca` (para classificação de robustez) e `mensagens` (para a lista de mensagens explicativas de erro/orientação), tanto na história de usuário US3, no requisito funcional FR-010 quanto nas entidades de domínio (`ResultadoValidacao`).
- **Ponto 2 (Tratamento de entradas inválidas / não texto):** Qual comportamento adotar para entradas nulas (`None`) ou tipos não string?
  - **Decisão/Resposta:** Definido comportamento determinístico único sem levantamento de exceções não tratadas: o validador retorna um resultado estruturado com `is_valid: False`, `forca: "FRACA"`, com o critério de tipo/entrada marcado como não atendido e orientação em `mensagens` informando que o valor informado deve ser uma string, garantindo resiliência para a aplicação chamadora (alinhamento em US4 e FR-012).

---

## 3. Histórias de Usuário Priorizadas

### US1 [P1] — Validação de Requisitos Estruturais de Complexidade
**Como** sistema integrador,  
**Quero** validar se uma senha atende às regras estruturais de composição (comprimento mínimo, maiúsculas, minúsculas, números e caracteres especiais),  
**Para** garantir que os usuários definam senhas com variedade suficiente de caracteres contra ataques de força bruta.

#### Cenários de Aceite (Dado / Quando / Então):

- **Cenário 1.1: Senha atende a todos os critérios estruturais**
  - **Dado** que uma senha possui comprimento de 10 caracteres,
  - **E** contém letras maiúsculas (`A-Z`), minúsculas (`a-z`), dígitos numéricos (`0-9`) e caracteres especiais (ex.: `!`),
  - **Quando** o validador processa a senha,
  - **Então** todos os critérios estruturais devem ser marcados como atendidos.

- **Cenário 1.2: Senha com comprimento inferior ao mínimo**
  - **Dado** uma senha com menos de 8 caracteres (ex.: `"Ab1!x"` com 5 caracteres),
  - **Quando** o validador processa a senha,
  - **Então** o critério de tamanho mínimo deve ser marcado como não atendido,
  - **E** o resultado geral de validação deve ser inválido (`is_valid = False`),
  - **E** uma mensagem indicando a necessidade de no mínimo 8 caracteres deve ser gerada.

- **Cenário 1.3: Senha sem letras maiúsculas**
  - **Dado** uma senha com mais de 8 caracteres contendo minúsculas, números e especiais, porém nenhuma maiúscula (ex.: `"senha123!"`),
  - **Quando** o validador processa a senha,
  - **Então** o critério de letra maiúscula deve ser marcado como não atendido,
  - **E** o resultado geral de validação deve ser inválido (`is_valid = False`).

- **Cenário 1.4: Senha sem letras minúsculas**
  - **Dado** uma senha com mais de 8 caracteres contendo maiúsculas, números e especiais, porém nenhuma minúscula (ex.: `"SENHA123!"`),
  - **Quando** o validador processa a senha,
  - **Então** o critério de letra minúscula deve ser marcado como não atendido,
  - **E** o resultado geral de validação deve ser inválido (`is_valid = False`).

- **Cenário 1.5: Senha sem dígitos numéricos**
  - **Dado** uma senha com mais de 8 caracteres contendo maiúsculas, minúsculas e especiais, porém nenhum número (ex.: `"SenhaForte!"`),
  - **Quando** o validador processa a senha,
  - **Então** o critério de dígitos numéricos deve ser marcado como não atendido,
  - **E** o resultado geral de validação deve ser inválido (`is_valid = False`).

- **Cenário 1.6: Senha sem caracteres especiais**
  - **Dado** uma senha com mais de 8 caracteres contendo maiúsculas, minúsculas e números, porém nenhum caractere especial (ex.: `"SenhaForte123"`),
  - **Quando** o validador processa a senha,
  - **Então** o critério de caracteres especiais deve ser marcado como não atendido,
  - **E** o resultado geral de validação deve ser inválido (`is_valid = False`).

---

### US2 [P1] — Identificação e Rejeição de Senhas Triviais e Padrões Simples
**Como** analista de segurança,  
**Quero** que o validador identifique e reprove senhas baseadas em termos conhecidos, sequências simples ou repetições excessivas,  
**Para** impedir o uso de senhas previsíveis e facilmente exploráveis por dicionário.

#### Cenários de Aceite (Dado / Quando / Então):

- **Cenário 2.1: Senha trivial ou de dicionário comum**
  - **Dado** uma senha pertencente à lista em memória de senhas triviais (ex.: `"Password123!"`, `"admin1234@"`, `"qwerty123!"`),
  - **Quando** o validador processa a senha,
  - **Então** a regra de verificação de senhas triviais deve ser marcada como violada,
  - **E** o status geral da validação deve ser inválido (`is_valid = False`),
  - **E** uma orientação específica alertando sobre o uso de senha comum/trivial deve ser fornecida.

- **Cenário 2.2: Senha contendo sequências alfanuméricas previsíveis**
  - **Dado** uma senha que contenha uma sequência consecutiva de 3 ou mais números ou letras (ex.: `"123"`, `"abc"`, `"xyz"`, `"987"`) em qualquer posição (ex.: `"Abc!98765"` ou `"Senha!123x"`),
  - **Quando** o validador processa a senha,
  - **Então** a regra de sequências simples deve ser marcada como violada,
  - **E** a senha deve ser marcada como inválida (`is_valid = False`).

- **Cenário 2.3: Senha com repetição excessiva de caracteres idênticos**
  - **Dado** uma senha que contenha 3 ou mais caracteres idênticos consecutivos (ex.: `"Aaaa!1234"` ou `"Senha!!!12"`),
  - **Quando** o validador processa a senha,
  - **Então** a regra de repetição de caracteres deve ser marcada como violada,
  - **E** a senha deve ser marcada como inválida (`is_valid = False`).

- **Cenário 2.4: Senha com variedade de caracteres sem sequências triviais**
  - **Dado** uma senha que combina elementos sem sequências consecutivas ou termos comuns (ex.: `"K9#mQ2$pL8"`),
  - **Quando** o validador processa a senha,
  - **Então** as regras de senhas triviais, sequências simples e repetições consecutivas devem ser marcadas como atendidas.

---

### US3 [P2] — Apresentação do Resultado Estruturado e Compreensível
**Como** usuário final ou desenvolvedor integrador,  
**Quero** receber um relatório estruturado contendo status geral, avaliação de força no campo `forca`, detalhamento por critério e orientações de correção no campo `mensagens`,  
**Para** entender perfeitamente os pontos de vulnerabilidade da senha e saber como ajustá-la com base em um contrato estável.

#### Cenários de Aceite (Dado / Quando / Então):

- **Cenário 3.1: Validação com feedback detalhado para senha aprovada**
  - **Dado** uma senha válida e complexa (ex.: `"C0mplex@Pass#2026"`),
  - **Quando** a validação é executada,
  - **Então** o objeto de resultado deve conter:
    - `is_valid` igual a `True`,
    - `forca` igual a `"FORTE"`,
    - lista detalhada com cada uma das regras e status individual `"aprovado"`,
    - `mensagens` como lista vazia (`[]`).

- **Cenário 3.2: Validação com múltiplas pendências e mensagens corretivas**
  - **Dado** uma senha que viola múltiplos critérios (ex.: `"abc"`),
  - **Quando** a validação é executada,
  - **Então** o objeto de resultado deve conter:
    - `is_valid` igual a `False`,
    - `forca` igual a `"FRACA"`,
    - indicação precisa de cada regra não atendida,
    - `mensagens` contendo lista de mensagens em linguagem natural orientando cada correção necessária (ex.: "A senha deve ter no mínimo 8 caracteres", "A senha deve conter ao menos uma letra maiúscula", "Evite sequências previsíveis como 'abc'").

- **Cenário 3.3: Classificação da força da senha**
  - **Dado** o conjunto de regras avaliadas,
  - **Quando** a pontuação de força for calculada,
  - **Então** a senha deve ser classificada objetivamente em seu campo `forca`:
    - `"FRACA"`: não atende aos requisitos mínimos obrigatórios ou contém padrões triviais/sequências simples;
    - `"MEDIA"`: atende aos requisitos mínimos obrigatórios com tamanho entre 8 e 11 caracteres;
    - `"FORTE"`: atende a todos os requisitos obrigatórios, não contém padrões fracos e possui tamanho igual ou superior a 12 caracteres com ampla diversidade de caracteres.

---

### US4 [P3] — Resiliência de Entradas e Casos de Borda
**Como** desenvolvedor integrador,  
**Quero** que o validador processe com segurança valores vazios, espaços, caracteres Unicode e tipos inválidos retornando um resultado estruturado consistente,  
**Para** que a aplicação não gere comportamentos indefinidos, falhas catastróficas ou erros de tempo de execução não tratados.

#### Cenários de Aceite (Dado / Quando / Então):

- **Cenário 4.1: Entrada nula ou com tipo incompatível**
  - **Dado** uma entrada `None`, número inteiro, booleano ou qualquer tipo não textual,
  - **Quando** a função de validação for acionada,
  - **Então** o validador deve retornar um resultado estruturado de validação inválida,
  - **E** com `is_valid` igual a `False`,
  - **E** com `forca` igual a `"FRACA"`,
  - **E** com `mensagens` contendo orientação clara de que o valor fornecido deve ser uma cadeia de texto (string), sem lançar exceções não tratadas para a aplicação chamadora.

- **Cenário 4.2: Entrada vazia ou exclusivamente com espaços**
  - **Dado** uma entrada vazia `""` ou contendo apenas caracteres de espaço `"   "`,
  - **Quando** a validação é executada,
  - **Então** deve retornar `is_valid = False`,
  - **E** `forca` igual a `"FRACA"`,
  - **E** `mensagens` contendo mensagem indicando que a senha não pode ser vazia ou composta unicamente por espaços.

- **Cenário 4.3: Senha longa ou formato passphrase com espaços intermediários**
  - **Dado** uma senha com espaços intermediários válidos (ex.: `"Cavalo Azul Salta $123"`),
  - **Quando** a validação é executada,
  - **Então** os espaços intermediários devem ser aceitos como caracteres válidos,
  - **E** a contagem de comprimento deve preservar os espaços internos.

- **Cenário 4.4: Suporte a caracteres acentuados e símbolos Unicode**
  - **Dado** uma senha contendo caracteres acentuados ou símbolos (ex.: `"Coração!Seguro#2026"`),
  - **Quando** a validação é executada,
  - **Então** os caracteres devem ser avaliados adequadamente sem quebras de codificação ou erros de decodificação.

---

## 4. Requisitos Funcionais

| ID | Descrição do Requisito | Regra de Negócio / Detalhe | Histórias Vinculadas |
|---|---|---|---|
| **FR-001** | Validação de comprimento mínimo | A senha deve possuir comprimento mínimo de 8 caracteres. Comprimentos inferiores a 8 reprovam a validação imediatamente. | US1, US3 |
| **FR-002** | Validação de letras minúsculas | A senha deve conter pelo menos uma letra minúscula (`a-z` ou equivalente alfabético minúsculo). | US1, US3 |
| **FR-003** | Validação de letras maiúsculas | A senha deve conter pelo menos uma letra maiúscula (`A-Z` ou equivalente alfabético maiúsculo). | US1, US3 |
| **FR-004** | Validação de dígitos numéricos | A senha deve conter pelo menos um dígito numérico decimal (`0-9`). | US1, US3 |
| **FR-005** | Validação de caracteres especiais | A senha deve conter pelo menos um caractere especial (símbolo não alfanumérico, pontuação ou caractere especial). | US1, US3 |
| **FR-006** | Detecção de senhas triviais e de dicionário | O validador deve confrontar a senha contra um catálogo imutável em memória de senhas triviais e termos conhecidos vulneráveis (ex.: "password", "senha", "admin", "qwerty", "123456", "mudar123"), de forma insensível a maiúsculas/minúsculas. | US2, US3 |
| **FR-007** | Detecção de sequências alfanuméricas simples | O validador deve identificar e rejeitar sequências alfabéticas ou numéricas consecutivas com 3 ou mais caracteres seguidos em ordem direta ou reversa (ex.: "123", "321", "abc", "cba"). | US2, US3 |
| **FR-008** | Detecção de repetições consecutivas idênticas | O validador deve identificar e rejeitar sequências de 3 ou mais caracteres idênticos consecutivos (ex.: "aaa", "111", "###"). | US2, US3 |
| **FR-009** | Classificação de força da senha | O validador deve classificar a senha no atributo `forca` em três níveis: `FRACA`, `MEDIA` e `FORTE`, baseando-se no cumprimento de regras obrigatórias, tamanho total da senha e diversidade de caracteres. | US3 |
| **FR-010** | Relatório estruturado de validação | O resultado retornado deve conter uma estrutura unificada com: `is_valid: bool`, `forca: str`, `criterios: list` (com nome, status atendido/não atendido e mensagem) e `mensagens: list[str]` (lista consolidada de recomendações e erros em linguagem natural). | US3 |
| **FR-011** | Suporte a passphrases e espaços internos | O validador deve permitir espaços intermediários na senha, preservando-os na contagem de caracteres e cálculo de entropia, desde que a senha não consista exclusivamente de espaços. | US4 |
| **FR-012** | Tratamento seguro de tipos e entradas anômalas | O validador deve tratar entradas nulas (`None`) e tipos não textuais retornando um objeto estruturado de validação inválida (`is_valid = False`, `forca = "FRACA"` e orientação em `mensagens`), sem propagar exceções não tratadas para a aplicação chamadora. | US4 |

---

## 5. Critérios de Sucesso e Requisitos Não Funcionais

| ID | Critério de Sucesso | Métrica Mensurável |
|---|---|---|
| **SC-001** | Independência e Ausência de Dependências Externas | 100% do código deve utilizar estritamente a biblioteca padrão do Python (`standard library`). Nenhuma biblioteca externa (`pip`), banco de dados ou requisição de rede/API deve ser utilizada. |
| **SC-002** | Desempenho e Eficiência | O tempo total de validação de qualquer senha de até 128 caracteres deve ser inferior a **5 milissegundos** em execução local padrão. |
| **SC-003** | Determinismo e Imutabilidade | Para qualquer senha fornecida, execuções repetidas devem retornar exatamente o mesmo resultado e o validador não deve manter estado mutável compartilhado entre invocações. |
| **SC-004** | Cobertura de Testes Automatizados | 100% dos requisitos funcionais (`FR-001` a `FR-012`) e todos os cenários de aceite das histórias de usuário devem possuir casos de testes automatizados associados. |
| **SC-005** | Clareza e Compreensibilidade das Mensagens | Todas as regras não atendidas devem produzir mensagens explicativas em língua portuguesa (pt-BR), orientando a ação necessária para correção através do campo `mensagens`. |

---

## 6. Entidades-Chave e Conceitos de Domínio

- **`Senha` (Password):**
  - Sequência textual fornecida para avaliação de conformidade.
- **`NivelForca` (StrengthLevel):**
  - Enumeração ou categorização do nível de robustez da senha:
    - `FRACA`: Não cumpre requisitos mínimos obrigatórios ou contém termos triviais/sequências óbvias.
    - `MEDIA`: Cumpre todos os requisitos obrigatórios, mas possui tamanho entre 8 e 11 caracteres.
    - `FORTE`: Cumpre todos os requisitos obrigatórios, possui 12 ou mais caracteres e não apresenta padrões fracos.
- **`ResultadoCriterio` (CriterionResult):**
  - Representa o resultado de um critério individual:
    - `codigo`: Identificador mnemônico da regra (ex.: `TAMANHO_MINIMO`, `MAIUSCULAS`, `MINUSCULAS`, `NUMEROS`, `ESPECIAIS`, `SENHA_TRIVIAL`, `SEQUENCIA_SIMPLES`, `REPETICAO_CARACTERES`, `TIPO_ENTRADA`).
    - `descricao`: Texto legível do critério.
    - `atendido`: Booleano (`True` se aprovado, `False` se reprovado).
    - `mensagem`: Mensagem amigável com a orientação pertinente.
- **`ResultadoValidacao` (ValidationResult):**
  - Estrutura completa retornada pela validação:
    - `is_valid`: Booleano consolidado (`True` se todos os critérios obrigatórios forem atendidos e não houver violações de segurança).
    - `forca`: Nível de força (`FRACA`, `MEDIA`, `FORTE`).
    - `criterios`: Lista de objetos `ResultadoCriterio`.
    - `mensagens`: Lista consolidada de mensagens de orientação para os critérios que não foram atendidos (vazia quando válida).

---

## 7. Casos de Borda e Condições Limítrofes

1. **Entrada nula (`None`) ou tipos não string (int, bool, float, etc.):** Deve retornar resultado estruturado com `is_valid = False`, `forca = "FRACA"` e mensagem informativa em `mensagens`, sem propagar exceção não tratada ao chamador.
2. **Entrada vazia (`""`):** Deve ser reprovada com `is_valid = False`, `forca = "FRACA"` e mensagem em `mensagens`.
3. **Entrada apenas com espaços (`"     "`):** Não deve ser aceita como senha válida, retornando `is_valid = False`, `forca = "FRACA"` e mensagem explicativa em `mensagens`.
4. **Senha com exatamente 7 caracteres:** Deve falhar na regra de tamanho mínimo (limite inferior da fronteira).
5. **Senha com exatamente 8 caracteres com todos os requisitos:** Deve ser aprovada com `is_valid = True` e `forca = "MEDIA"`.
6. **Senha com exatamente 12 caracteres com todos os requisitos:** Limiar para elegibilidade à classificação `forca = "FORTE"`.
7. **Senhas longas (passphrases com 64 a 128 caracteres):** Devem ser processadas eficientemente sem estouro de memória ou lentidão.
8. **Sequências reversas (ex.: `"fedcba"`, `"98765"`):** Devem ser identificadas da mesma forma que sequências diretas (`"abcdef"`, `"12345"`).
9. **Caracteres especiais repetidos (ex.: `"!!!!!"`):** Devem disparar a regra de repetição de caracteres consecutivos.
10. **Caracteres acentuados ou Unicode (ex.: `"ã"`, `"ç"`, `"é"`):** Devem ser reconhecidos como caracteres alfabéticos válidos de acordo com suas propriedades Unicode.

---

## 8. Premissas e Restrições do Projeto

- **Premissa 1:** A solução deve ser implementada em Python 3 puro (versão 3.10+ recomendada), utilizando módulos da biblioteca padrão (ex.: `re`, `dataclasses`, `enum`, `typing`, `string`).
- **Premissa 2:** Não haverá persistência em banco de dados; listas de senhas fracas ou sequências devem ser gerenciadas em estruturas imutáveis em memória (`frozenset`, `tuple`).
- **Premissa 3:** Não haverá comunicação com serviços externos ou APIs de verificação de senhas comprometidas (ex.: HaveIBeenPwned). O validador opera de maneira autônoma e autocontida.
- **Premissa 4:** A saída da validação deve ser um objeto/estrutura de dados tipada e previsível, mantendo o contrato estrito com os campos `is_valid`, `forca`, `criterios` e `mensagens`.
- **Premissa 5:** Todas as anotações auxiliares do ciclo de vida da feature devem ser armazenadas estritamente em `specs/001-validador-senhas/notes/`, respeitando a diretriz de raiz limpa da Fábrica de Software.
