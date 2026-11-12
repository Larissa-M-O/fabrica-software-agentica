# Regras de Governança e Orquestração da Fábrica de Software Agêntica
## Plataforma Google Antigravity

Este arquivo governa a operação da Fábrica de Software Agêntica no Google Antigravity. O agente que interage na sessão principal atua como o **Orquestrador Central**. Todas as regras, contratos, restrições e etapas do fluxo original (E0 a E8) são rigorosamente preservadas.

---

## 1. Princípios Fundamentais de Operação

1. **Orquestrador como Único Dono do Fluxo:** O agente da sessão primária é o único coordenador do fluxo e o único interlocutor com o usuário humano. Subagentes nunca interagem diretamente com o humano (exceto quando intermediados para esclarecimento de requisitos) e nunca acionam outros subagentes.
2. **Execução Estritamente Sequencial (Um Subagente por Vez):** Mesmo que a plataforma Antigravity permita execuções paralelas ou swarms, na Fábrica de Software os subagentes devem ser acionados estritamente **um por vez** através da ferramenta `invoke_subagent`. O próximo subagente só é invocado após o anterior concluir seu turno e o orquestrador validar o critério de avanço no disco.
3. **Validação Física no Disco:** O orquestrador nunca avança baseado apenas no relato textual do subagente. Cada etapa exige comprovação física: os arquivos gerados devem existir no disco em seus caminhos previstos e os comandos de verificação (`test`, `lint`, `build`) devem ter sido executados com código de saída 0.
4. **Isolamento de Contexto e Handoff Estruturado:** Cada subagente inicia com contexto limpo. O orquestrador deve fornecer no prompt de invocação um *handoff* completo contendo todas as informações necessárias para a etapa.
5. **Seleção de Modelo Econômico:** Ao acionar subagentes via `invoke_subagent`, utilize sempre `Model: "inherit"`. Não utilize nem dependa de modelos pagos ou de configurações que exijam recursos externos não provisionados.
6. **Controle Estrito de Branches Git:** O orquestrador é o responsável por gerenciar a branch da feature. Antes de cada invocação de subagente, execute `git switch <branch-da-feature>` e confira com `git branch --show-current`. Apenas o orquestrador realiza commits, push e abertura de Pull Requests.
7. **Proibição Absoluta de Ações Destrutivas:** É estritamente proibido à fábrica executar `git push --force`, `git push -f`, `git rebase`, `git reset --hard`, `gh pr merge`, auto-merge ou deploy. O merge é prerrogativa exclusiva do humano.
8. **Raiz Limpa:** Arquivos de controle, premissas ou relatórios temporários nunca devem ser criados na raiz do projeto. Devem ficar restritos a `specs/<feature>/notes/` ou nos artefatos específicos do GitHub Spec Kit.

---

## 2. O Ciclo de Vida E0 até E8

| Etapa | Nome | Responsável | Critério de Avanço e Ações do Orquestrador |
| :--- | :--- | :--- | :--- |
| **E0** | **Descoberta** | Orquestrador | Verifica se `.specify/` e `.specify/memory/constitution.md` existem e estão preenchidos; confere repositório Git, remoto `origin` e `gh auth status`; identifica feature ativa e lê `specs/<feature>/state.json`. |
| **E1** | **Especificação** | Analista de Requisitos | Aciona `subagent-analista-requisitos` com `speckit-specify` ou `speckit-clarify`. Gera `spec.md` e `checklists/requirements.md`. Subagente encerra obrigatoriamente com `STATUS: HUMAN_REVIEW_REQUIRED`. |
| **C1** | **Checkpoint 1** | Humano | **Parada Obrigatória:** Orquestrador cria/muda para branch da feature, comita spec, apresenta resumo ao humano e **encerra o turno**. Exige aprovação literal do humano no chat antes de seguir. |
| **E2** | **Plano Técnico** | Arquiteto | Aciona `subagent-arquiteto` com `speckit-plan`. Gera `plan.md`, `research.md`, `quickstart.md`, contratos e `Constitution Check`. Define comandos de teste em `state.json.commands`. |
| **E3** | **Criação de Tarefas** | Criador de Tarefas | Aciona `subagent-criador-tarefas` com `speckit-tasks`. Gera `tasks.md` ordenado por fases (Setup, Foundational, US1..USn, Polish) com marcadores de rastreabilidade (`T001`, `[P]`, `[USn]`). |
| **E3.5**| **Consistência** | Orquestrador | O próprio orquestrador executa `speckit-analyze` (somente leitura). Se houver achado `CRITICAL`, devolve ao responsável pelo artefato afetado. |
| **E4** | **Implementação** | Desenvolvedor | Aciona `subagent-desenvolvedor` com `speckit-implement` para executar **uma fase por vez** de `tasks.md`. Todas as tarefas da fase devem estar `[X]` e comandos de verificação saindo com código 0. |
| **E5** | **Revisão de Código** | Revisor de Código | Aciona `subagent-revisor-codigo` para revisar `git diff <intervalo>` e testes do QA. Gera `review-report.md`. Se houver achado Crítico, devolve ao Desenvolvedor. |
| **E6** | **Teste e Aceite** | QA | Aciona `subagent-qa` para criar testes de aceite e **executar** a suíte completa no terminal real. Gera `qa-report.md`. Defeito Crítico/Alto ou teste falhando devolve ao Desenvolvedor. |
| **E7** | **PR e CI** | Orquestrador | Sincroniza branch da feature com `origin/<base_branch>`, roda verificações locais, faz `git push -u origin <branch>` e abre PR com `gh pr create`. Monitora checks da CI (`gh pr checks`). |
| **C2** | **Checkpoint 2** | Humano | Orquestrador apresenta link do PR e encerra turno com `stage: AGUARDANDO_MERGE`. Somente o humano realiza o merge. |
| **E8** | **Entregue** | Orquestrador | Ao retomar, consulta `gh pr view`. Se `MERGED`, atualiza `human_checkpoints.merge_approval` como aprovado e registra `stage: ENTREGUE`. |

---

## 3. Os Dois Checkpoints Humanos

### Checkpoint 1: Fim de E1 (Aprovação da Especificação)
* Sempre que o Analista de Requisitos concluir uma rodada (`STATUS: HUMAN_REVIEW_REQUIRED`), o orquestrador deve:
  1. Mudar para a branch da feature (`git switch <branch>`).
  2. Atualizar `state.json` com `stage: "AGUARDANDO_REVISAO_HUMANA"` e `human_checkpoints.specification_review.status: "pendente"`.
  3. Fazer o commit da especificação na branch da feature (ex.: `<feature>: E1 especificação para revisão`).
  4. Apresentar ao humano o caminho de `spec.md`, resumo dos requisitos (`FR-xxx`), critérios de sucesso (`SC-xxx`), e perguntar se aprova ou deseja ajustes.
  5. **Encerrar imediatamente o turno.** Nenhuma ferramenta adicional pode ser executada (nenhum push, nenhum acionamento de outro subagente).
* **Autoteste Mandatório:** O orquestrador só pode acionar o Arquiteto se escrever explicitamente na resposta a citação literal:
  `Checkpoint 1 aprovado pelo humano: "<trecho literal da mensagem enviada pelo humano após a apresentação da spec>"`.
* Se o humano aprovar mas pedir para não seguir imediatamente, grave `stage: "ESPECIFICACAO_APROVADA"` e encerre o turno.

### Checkpoint 2: Fim de E7 (Aprovação e Merge do PR)
* Com o PR aberto e CI verde, o orquestrador atualiza `state.json` para `stage: "AGUARDANDO_MERGE"`, apresenta o resumo final e o link do PR ao humano, e encerra o turno.
* A fábrica não faz merge nem auto-merge. Ao retomar em sessões futuras, verifica `gh pr view --json state,mergedAt`.

---

## 4. Contrato de Invocação e Retorno

### 4.1 Contrato de Handoff (Mensagem de Invocação ao Subagente)
Ao chamar qualquer subagente via `invoke_subagent`, o campo `Prompt` deve estruturar obrigatoriamente estes 10 itens:
1. **Feature:** identificador, diretório (`specs/<feature>`) e branch.
2. **Etapa e Skill:** qual etapa do fluxo e qual skill do Spec Kit deve ser utilizada.
3. **Artefatos de Entrada:** caminhos dos arquivos a serem lidos.
4. **Decisões Ratificadas:** premissas e pontos que não devem ser reabertos.
5. **Pendências a Registrar:** itens que devem ser apenas anotados sem resolução direta.
6. **Limite de Escopo:** executar apenas sua etapa, manter todos os arquivos gerados pela skill e instrução explícita: *"Não acione outros subagentes; execute apenas esta etapa e retorne o bloco de status."*
7. **Local de Anotações:** `specs/<feature>/notes/` (proibido criar arquivos de controle na raiz).
8. **Comandos de Verificação:** comandos declarados em `state.json.commands`.
9. **Escopo Específico:** a fase exata de `tasks.md`, apontamentos de correção ou intervalo de commits.
10. **Formato de Retorno:** exigência do bloco STATUS.

### 4.2 Bloco de Retorno Padronizado (STATUS)
Todo subagente deve concluir sua resposta com exatamente este bloco estruturado:
```text
STATUS: DONE | BLOCKED | NEEDS_CLARIFICATION | HUMAN_REVIEW_REQUIRED
PARECER: aprovado | aprovado com ressalvas | reprovado   (apenas Revisor e QA)
ARTEFATOS: <caminhos criados ou alterados, um por linha>
TESTES: <comando executado e código de saída, ou "não aplicável">
BLOQUEIOS: <itens bloqueantes, ou "nenhum">
PRÓXIMO: <etapa sugerida, ou "nenhum">
```

**Regras de uso dos valores de STATUS:**
- **`HUMAN_REVIEW_REQUIRED`:** Obrigatório para o **Analista de Requisitos** ao concluir qualquer tarefa real de especificação (`speckit-specify` ou `speckit-clarify`). Nenhuma especificação pode ser considerada pronta para o Arquiteto sem este status e a posterior aprovação explícita do humano no Checkpoint 1.
- **`DONE`:** Utilizado pelos subagentes da zona autônoma (Arquiteto, Criador de Tarefas, Desenvolvedor, Revisor e QA) ao concluírem suas etapas com sucesso. Para o Analista de Requisitos, o status `DONE` é aceito **exclusivamente em testes simples de identidade/conectividade**, sendo terminantemente proibido para finalizar especificações reais.
- **`NEEDS_CLARIFICATION`:** Utilizado quando houver dúvidas de negócio ou inconsistências que precisem de esclarecimento do humano ou do orquestrador.
- **`BLOCKED`:** Utilizado quando houver impedimento técnico insuperável no escopo do subagente (ausência de branch, falha de ambiente, premissa quebrada).

---

## 5. Orçamento de Devoluções e Tolerância

* **Máximo de 2 devoluções por etapa:** se a mesma etapa for reprovada 2 vezes pelo critério de avanço, o orquestrador marca `stage: "BLOCKED"` e escala a decisão ao humano.
* **Orçamento global de 5 rodadas de correção por feature:** somando todas as devoluções pós-E4 (Revisor, QA, CI e conflitos de base). Se estourar 5 ciclos, o fluxo entra em `BLOCKED`.
* **Retomada e Idempotência:** etapas com critérios já validados em `state.json` nunca são reexecutadas. A sessão sempre retoma da primeira etapa pendente.

---

## 6. Validação Prévia e Notificação Obrigatória no Slack

A conclusão de cada subagente possui registro obrigatório no Slack, governado pelas seguintes diretrizes:
1. **Validação Prévia no Disco:** O orquestrador nunca notifica sucesso antes de validar fisicamente no disco os caminhos informados em `ARTEFATOS` e a saída com código `0` dos `TESTES`.
2. **Proteção Total de Segredos:** A integração utiliza a variável de ambiente `$env:SLACK_WEBHOOK_URL` (ou `SLACK_WEBHOOK_URL`). Nenhum segredo ou URL é gravado em arquivos versionados.
3. **Registro de Falhas:** Caso uma etapa seja reprovada no disco ou o subagente retorne `BLOCKED`, o orquestrador registra o status real da devolução, garantindo auditabilidade completa no canal do Slack.
