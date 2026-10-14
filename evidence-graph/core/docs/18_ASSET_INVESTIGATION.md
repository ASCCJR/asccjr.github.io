# M3 — investigação por ativo e publicação de avaliação

**Data:** 2026-10-14. **Base:** Grupo Aurora, revisão do PR #1.

## O que mudou

O grafo continua como entrada. Cada ativo oferece três ações: **De que depende?**, **Quem depende dele?** e **Qual operação está envolvida?**. O alcance pode ser direto, de até dois ou até quatro níveis. Quando há conexões além do limite, a interface informa isso.

Grafo e lista de exploração exibem os mesmos IDs, relações, filtros e seleção. A revisão de mudança é uma tarefa distinta: “Revisar este consumidor” filtra o resultado preparado; “Ver no grafo” devolve o foco ao ativo. Inventário, notas e exportação de análise continuam disponíveis. A exploração também exporta seu recorte em Markdown.

Os nomes de processos no painel são apresentação amigável dos vínculos explícitos do dataset. Não inventam associação de negócio. O nome Grupo Aurora é fictício; a explicação está em Sobre o ambiente e nos relatórios.

## Semântica e limites

`CALLS`, `READS`, `USES_TOOL`, `ROUTES_TO`, `USES_MODEL` e `TRAINED_ON` ligam consumidor a recurso usado. `WRITES` e `DERIVES_TO` são invertidas ao buscar a origem de dados. Identidade, estrutura de colunas e hospedagem não viram chamadas nem permissão.

A exploração calcula alcance tipado sobre vínculos do catálogo, sem reavaliar validade temporal das evidências nem inferir quebra de contrato. Relações entre ambientes distintos são excluídas. Processos compartilhados são associações, não dependências. O algoritmo evita duplicações e ciclos; contagens incluem o foco e mostram apenas o recorte filtrado.

As análises de impacto específicas continuam as três do Python M1. Uma lista maior de dependentes não significa uma quantidade maior de incompatibilidades. Não há coleta real, IAM efetivo, bloqueio, mensagens enviadas ou aprovação automática de deploy.

## Testes locais executados

- **43** testes da base M1, Python 3.13.5.
- **13** testes puros de exploração, Node 22.16.0: direção, lineage, origem por escrita, ciclos, limites, processos e isolamento de ambientes.
- **20** testes Chromium/Playwright: abertura, perguntas por ativo, profundidade, seleção compartilhada, filtros, retorno grafo/lista, notas em sessão, exportação, 240 ativos/512 relações, teclado, largura 1366 e estados inconclusivos.
- Inspeção de capturas em 1920 e 1366 pixels.

O navegador gerenciado bloqueou navegação HTTP local (`ERR_BLOCKED_BY_ADMINISTRATOR`); os testes de interface carregaram HTML/CSS/JS diretamente no DOM. Isso não comprova navegação hospedada nem persistência de localStorage em uma origem publicada. Notas em sessão e geração/download de Markdown foram testados; persistência entre recarregamentos precisa de verificação manual no endereço publicado.

Os testes antigos de M2 que esperavam que o botão “Lista” trocasse para a revisão de mudança foram substituídos pelos testes de contexto compartilhado. Não se afirma que aquela expectativa antiga continua válida.

## Publicação

A versão de avaliação deve ser publicada em `/evidence-graph/preview-m2/`, sem substituir `/evidence-graph/`. Os dados gerados devem estar presentes antes do merge: `data.js` e `manifest.json`. O workflow restrito à branch do PR #1 os gera, valida a base e os versiona. Não altera configurações globais do Pages nem cria uma página na raiz removida pelo proponente.

O status real do merge e da implantação deve ser consultado no PR e no Pages; este documento não prova que o deploy terminou. Não incluir material pessoal, modificar Campus Mobile ou alterar entregas acadêmicas.

## Verificação manual sugerida

Selecionar API de clientes; abrir “Quem depende dele?”; alternar Diretos/Até 2 níveis; trocar Grafo/Lista; selecionar Agente de atendimento; revisar o consumidor; registrar uma nota; exportar a análise; voltar ao grafo. Depois repetir com o dashboard de reposição e “De que depende?”.

Após recarregar o endereço publicado, conferir a nota local. Essa confirmação ainda não é validação de mercado. Próximo marco: sessões exploratórias com usuários e coleta real restrita, não outro redesenho.
