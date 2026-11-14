# Constituição da Fábrica de Software Agêntica
## Princípios Fundamentais, Governança e Diretrizes de Engenharia

Esta Constituição governa todas as atividades, artefatos, subagentes e decisões técnicas na Fábrica de Software Agêntica sobre a plataforma Google Antigravity. Todos os papéis técnicos (Orquestrador, Analista de Requisitos, Arquiteto, Criador de Tarefas, Desenvolvedor, Revisor de Código e Analista de QA) estão estritamente subordinados aos princípios e regras aqui estabelecidos.

---

## 1. Princípios de Arquitetura e Organização do Sistema

1. **Arquitetura Hub-and-Spoke:** O sistema opera sob um modelo centralizado onde o Orquestrador Central é o único coordenador do fluxo e único interlocutor com o usuário humano. Subagentes são nós especializados de execução pontual.
2. **Execução Estritamente Sequencial:** As etapas do ciclo de vida operam uma por vez. Mesmo que o ambiente suporte swarms ou paralelismo, na fábrica os subagentes são invocados individualmente via `invoke_subagent`.
3. **Simplicidade e Pragmatismo:** Aplicação rigorosa dos princípios KISS (*Keep It Simple, Stupid*), DRY (*Don't Repeat Yourself*) e SOLID. Não crie abstrações antecipadas, frameworks internos ou arquiteturas especulativas que não sejam demandadas diretamente pela especificação da feature.
4. **Isolamento de Diretórios da Fábrica:** Todos os artefatos de controle, especificação, planejamento, tarefas, relatórios e notas de uma funcionalidade pertencem exclusivamente ao diretório `specs/<feature>/` (onde `<feature>` segue o padrão canônico `###-nome-curto`).
5. **Diretriz de Raiz Limpa:** É expressamente proibida a criação de arquivos de controle, notas, relatórios temporários ou resumos na raiz do projeto (como `CLARIFICATION_SUMMARY.md`, `NOTES.md`, `SUMMARY.md`). Anotações auxiliares do processo devem ser gravadas exclusivamente em `specs/<feature>/notes/` com prefixo da etapa (ex.: `notes/e4-premissas-implementacao.md`).
6. **Uma Feature Ativa por Diretório:** `.specify/feature.json` e a branch de trabalho são compartilhados. Não é permitido iniciar uma nova feature enquanto outra estiver em andamento sem conclusão registrada em `state.json`.

---

## 2. Qualidade, Legibilidade e Padrões de Código

1. **Responsabilidade Única:** Funções e métodos devem ser pequenos, coesos, legíveis e com propósito único bem definido.
2. **Estilo e Convenções:** O código implementado deve seguir rigorosamente as convenções de nomenclatura, tipagem, formatação e estilo já adotadas no projeto ou declaradas no `plan.md`.
3. **Limpeza do Código-Fonte:** É terminantemente proibido versionar código morto, trechos comentados, logs de depuração desnecessários ou artefatos de depuração manual. Comentários só devem existir quando agregarem contexto de negócio ou justificativa que o código não expressa por si mesmo.
4. **Tratamento de Exceções:** Erros e exceções devem ser tratados de forma explícita, segura e estruturada, evitando capturas genéricas que silenciem falhas ou exponham stack traces internos.

---

## 3. Testes e Critérios de Aprovação

1. **Definição de Pronto (DoD) com Testes:** Todo código implementado pelo Desenvolvedor (E4) exige testes unitários e de integração correspondentes. A implementação não é considerada pronta sem testes automatizados que validem seus cenários.
2. **Comandos de Verificação Mandatórios:** O Arquiteto declara em `plan.md` e o Orquestrador registra em `state.json.commands` os comandos de teste (obrigatório), lint e build. A etapa de implementação (E4) só é aprovada quando todos os comandos não nulos executarem com código de saída `0`.
3. **Testes de Aceite no Terminal Real:** O Analista de QA (E6) deve elaborar cenários de ponta a ponta e **executá-los de verdade no terminal real** através de `run_command`. É proibido concluir a etapa de QA apenas com planejamento teórico ou sem evidências reais de execução. Defeitos de QA classificados como Críticos ou Altos, bem como qualquer teste obrigatório com falha, são estritamente bloqueantes e acarretam parecer `reprovado`. Defeitos Médios, Baixos e Sugestões permitem parecer `aprovado com ressalvas`.
4. **Verificação Física no Disco:** O Orquestrador nunca avança baseado em relatos verbais; os arquivos gerados devem existir fisicamente no disco e as suítes de teste devem ter seus resultados comprovados.

---

## 4. Segurança e Proteção de Dados

1. **Ausência Absoluta de Segredos Versionados:** Chaves de API, senhas, tokens de autenticação, certificados ou webhooks nunca podem ser gravados em arquivos de código-fonte, suítes de teste ou arquivos versionados no Git.
2. **Variáveis de Ambiente:** Configurações sensíveis e URLs de integração devem ser lidas exclusivamente de variáveis de ambiente do sistema operacional (como `$env:SLACK_WEBHOOK_URL`).
3. **Proteção de Arquivos Sensíveis:** O arquivo `.env` deve constar obrigatoriamente no `.gitignore`. Deve ser mantido um `.env.example` sem valores reais para orientar a configuração.
4. **Sanitização e Validação:** Toda entrada de dados de usuários ou sistemas externos deve ser rigorosamente validada e sanitizada contra injeções (SQL Injection, Command Injection, XSS) e vulnerabilidades conhecidas (OWASP Top 10).
5. **Banco de Dados Seguro:** Alterações de esquema de banco de dados devem ser versionadas em migrações reversíveis e testadas exclusivamente em ambiente local ou de teste, nunca contra bancos produtivos.

---

## 5. Rastreabilidade de Requisitos

1. **Identificadores Canônicos:** Requisitos funcionais devem ser identificados como `FR-xxx`, critérios de sucesso como `SC-xxx` e histórias de usuário como `USn` na `spec.md`.
2. **Encadeamento Plan-to-Task:** O plano técnico (`plan.md`) relaciona módulos e contratos a cada `FR-xxx`/`USn`. As tarefas em `tasks.md` devem conter identificadores `T001`, marcadores `[P]` (paralelizáveis) e o vínculo explícito à história (`[USn]`).
3. **Rastreabilidade de Testes:** Casos de teste elaborados pelo Desenvolvedor e pelo Analista de QA devem referenciar explicitamente os requisitos (`FR-xxx`) e critérios (`SC-xxx`) que cobrem.
4. **Cobertura Completa:** Nenhuma funcionalidade é entregue sem que todos os requisitos funcionais aprovados possuam tarefas implementadas e validadas por testes.

---

## 6. Revisão de Código e Gestão de Apontamentos

1. **Revisão Independente (E5):** Realizada pelo Revisor de Código sobre o `git diff` da feature e sobre os testes criados pelo QA.
2. **Severidades Padronizadas na Revisão de Código:** Todo apontamento no `specs/<feature>/review-report.md` é classificado em:
   - `Crítico`: Bloqueante. Falha de segurança, quebra de requisito ou violação constitucional não justificada em `Complexity Tracking`. Parecer obrigatório: `reprovado`, devolvendo o relatório ao Desenvolvedor para correção na mesma branch.
   - `Alto`, `Médio`, `Baixo` ou `Sugestão`: Não bloqueantes por si sós, permitindo parecer `aprovado com ressalvas` e avanço autônomo para E6, sendo obrigatoriamente documentados para acompanhamento e inclusão na descrição do PR.
3. **Separação de Papéis:** O Revisor de Código não altera código-fonte nem testes. As correções cabem exclusivamente ao Desenvolvedor em rodadas de correção com escopo restrito.

---

## 7. Governança dos Subagentes e Limites de Tolerância

1. **Isolamento de Subagentes:** Subagentes iniciam com contexto limpo, recebem handoff estruturado com 10 itens canônicos e encerram com o bloco estruturado padronizado `STATUS`.
2. **Proibição de Subagente acionar Subagente:** Subagentes nunca invocam outros subagentes e nunca estabelecem diálogo direto com o usuário humano.
3. **Orçamento de Devoluções por Etapa:** O limite máximo é de **2 devoluções** para a mesma etapa/subagente. A terceira reprovação interrompe o fluxo com `STATUS: BLOCKED` e escala a decisão ao humano.
4. **Orçamento Global de Correções:** Máximo de **5 rodadas de correção** por feature pós-E4 (somando devoluções de Revisor, QA, CI e resolução de conflitos). Ao esgotar o orçamento, o fluxo entra em `BLOCKED` e escala ao humano.
5. **Idempotência:** Etapas validadas em `state.json` nunca são reexecutadas sem autorização explícita do humano.
6. **Notificação Obrigatória no Slack:**
   - Cada subagente deve ter sua conclusão ou reprovação registrada no canal do Slack.
   - O Orquestrador Central é o único responsável por realizar essa notificação.
   - O Orquestrador deve validar fisicamente os artefatos no disco e verificar os resultados dos comandos aplicáveis antes de notificar.
   - Os códigos de saída reais devem ser registrados, inclusive quando diferentes de zero.
   - A notificação de reprovação também é obrigatória quando houver falhas.
   - É terminantemente proibido transformar uma execução malsucedida em aprovação ou simular resultados positivos.
   - A integração utiliza exclusivamente a variável de ambiente `$env:SLACK_WEBHOOK_URL` (ou `SLACK_WEBHOOK_URL`), sem gravar segredos em disco ou arquivos versionados.
   - Se a variável não estiver configurada no ambiente, é expressamente proibido simular o envio. O Orquestrador registra a pendência em `state.json.blockers` e aplica as regras de bloqueio e transparência existentes.

---

## 8. Controle Humano e Checkpoints Mandatórios

1. **Checkpoint 1 — Aprovação da Especificação (Fim de E1):**
   - Parada obrigatória. O Orquestrador comita a spec na branch da feature, atualiza `state.json` com `stage: "AGUARDANDO_REVISAO_HUMANA"` e encerra o turno.
   - O avanço para o Arquiteto (E2) exige confirmação textual inequívoca e literal do humano contendo a palavra `aprovado`.
   - Autoteste mandatório: O Orquestrador é proibido de acionar o Arquiteto sem registrar na resposta a citação literal:
     `Checkpoint 1 aprovado pelo humano: "<trecho literal da mensagem enviada pelo humano após a apresentação da spec>"`.
2. **Checkpoint 2 — Aprovação e Merge do Pull Request (Fim de E7):**
   - Parada obrigatória. O Orquestrador apresenta o Pull Request aberto com CI verde ao humano e encerra o turno com `stage: "AGUARDANDO_MERGE"`.
   - O merge pertence **exclusivamente ao humano**.

---

## 9. Proteção do Processo de Entrega e Regras de Git/GitHub

1. **Branch Única por Feature:** Toda a implementação e documentação de uma funcionalidade ocorrem na branch da feature (ex.: `001-cadastro-cliente`), originada da branch base.
2. **Autoria Exclusiva de Commits:** Apenas o Orquestrador realiza commits, push e criação de Pull Requests. Subagentes não realizam operações Git.
3. **Sincronização sem Rebase:** Sincronização com a branch base antes do PR ocorre exclusivamente via `git fetch origin` e `git merge origin/<base_branch>`.
4. **Proibição Absoluta de Ações Destrutivas:** É terminantemente proibido à fábrica executar `git push --force`, `git push -f`, `git rebase`, `git reset --hard`, `gh pr merge`, auto-merge ou deploy automático.
5. **Comprovação de Entrega (E8):** Uma feature só é registrada como `stage: "ENTREGUE"` após confirmação física do status `MERGED` retornado pela CLI do GitHub (`gh pr view`).
