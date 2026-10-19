# L7 — níveis de evidência na experiência existente

**Data original:** 2026-10-17. **Base:** `09a1d42cce8506d0e7a801fd191914c4fdbfd142`.
**Integração local:** 2026-10-19; alterações ainda não enviadas ao PR #3, sem commit/push/merge/deploy. Sites e candidatura CTE-IA não fazem parte desta etapa.

## Entrega

A pasta `core/review-ui/` apresenta a L6-B sobre os componentes visuais M3. O grafo continua como entrada. Painel do ativo, detalhes, tabela e relatório distinguem **indício**, **inferência sob hipóteses** e **resultado de teste**. O código experimental de inferência não foi ampliado ou promovido ao analisador geral do produto.

As fontes são separadas: **Aurora Revisão** (12 consumidores + resposta da API, 12 relações), **Aurora Validação** (8 consumidores + resposta, 8 relações) e **Grupo Aurora** (240 ativos/512 relações preservados). Os nomes amigáveis são mapeamentos explícitos. As relações `USES_RESPONSE` significam consumo da resposta na fixture; não afirmam descoberta de chamadas HTTP autônomas. Equipes, processos e criticidade não foram inferidos.

O builder verifica hashes da execução L6-B fornecida, recalcula previsões dos inputs anteriores e compara-as com as registradas. Resultados dos testes posteriores são carregados separadamente. A caixa **Mostrar testes registrados** revela esses resultados históricos; não executa código nem modifica a previsão. É revelação progressiva, não segurança: os dados fictícios estão no HTML.

## Exemplos verificáveis

- **Consulta resiliente (c06):** leitura do campo observada; nenhuma exceção prevista no subconjunto reconhecido; teste registrado concluiu sem exceção. Não há avaliação de requisito de negócio neste caso.
- **Consulta condicional (c10):** inferência permanece inconclusiva porque a sintaxe não é reconhecida; teste posterior registrou exceção. O resultado não é usado retroativamente como acerto do preditor.
- **Pedido identificado (n01) e Consulta anônima (n02):** mesmo código de fallback, nenhuma exceção prevista; o requisito é violado em n01 e atendido em n02, conforme as expectativas explícitas do avaliador.

Notas e verificações manuais não alteram esses estados. Exportação segue os filtros e registra se os resultados posteriores foram incluídos. Sem a opção marcada, não inclui os ponteiros das referências posteriores no relatório. Fontes ficam isoladas também nas chaves de armazenamento das notas.

## Condição de inicialização investigada

O core anterior chamava `boot()` de forma imediata e descomprimia os dados de forma assíncrona. As extensões, carregadas em scripts defer posteriores, registravam ouvintes de `eg:ready`. A leitura aponta uma possível condição de corrida: o core pode terminar antes do registro de uma extensão atrasada, deixando o seletor sem comportamento mesmo quando outros componentes aparecem. A hipótese é compatível com o timeout anterior; sua reprodução HTTP e a causa daquele timeout permanecem sem comprovação nesta integração.

`lab-runtime/view_lifecycle.py` passa a preparar as cópias geradas: o core expõe `EGStart`; um script final inicia a aplicação depois de todas as extensões terem registrado os ouvintes. O seletor começa desabilitado e só é liberado após o evento de conclusão dos componentes. Foram adaptados **os builders** L3/L5, não os fontes publicados em `preview-m2/` nem capturas antigas.

A suíte HTTP contém uma fixture que reconstrói o padrão antigo. Um gate no servidor retém a resposta real de `auth_view.js` até o teste observar `eg:ready` no padrão antigo, ou `EGStart` definido sem prontidão no padrão corrigido. Só então libera a extensão. O limite de espera causa falha; não substitui a ordem observada por uma pausa fixa. A versão corrigida também verifica trocas repetidas e um único evento de prontidão por navegação. A execução dessa reprodução continua pendente enquanto o navegador correspondente não puder ser instalado; não confirma a causa do timeout histórico.

## Testes e limites

**Histórico de 2026-10-17, não resultado desta integração:** o pacote registra 249 testes Python aprovados (124 regressões do laboratório, 43 L6-A, 62 L6-B, 20 do builder/revisão), verificações por DOM e uma tentativa HTTP bloqueada com `ERR_BLOCKED_BY_ADMINISTRATOR`. O manifesto e os logs históricos não demonstram execução HTTP bem-sucedida.

O workflow L7 está apenas na árvore local. Sua presença configura uma execução futura; não comprova execução no GitHub Actions. Os runs remotos consultados no Checkpoint 1 pertencem ao HEAD L6-B: avaliação `38947283075` aprovada e interface `38947283060` aprovada na segunda tentativa, preservando a primeira tentativa falha. Não há novo CI remoto desta integração, pois não haverá push nesta etapa.

**Ambiente local de 2026-10-19:** Python 3.12 em ambiente virtual dedicado, requisitos declarados e Playwright 1.57.0 instalados. O instalador do Chromium correspondente recusou o Ubuntu 26.04 (`Playwright does not support chromium on ubuntu26.04-x64`). Não foi alterada a identificação da plataforma, usada outra versão de navegador ou desabilitada proteção para contornar esse bloqueio. Resultados locais e pendências ficam registrados no Checkpoint 2; nenhum resultado de navegador deve ser inferido dos testes Python.

**Resultados locais desta integração:** 124 regressões do laboratório, 43 L6-A e 62 L6-B passaram. A primeira execução de 20 testes L7 teve 16 aprovações e quatro erros por uma correspondência de texto incorreta na alteração adicional do exportador. Corrigido esse trecho, os 20 testes L7 passaram. São 249 testes distintos aprovados; a repetição de 20 testes não amplia essa contagem. Ambos os resultados foram preservados, sem relaxar asserções.

A suíte HTTP L7 passou a definir 14 casos: acrescenta exportação do grafo por fonte e notas entre duas capturas L7. As anteriores definem 12 casos L3 e dez L5: 36 casos distintos previstos. Nenhum caso de navegador executou. A primeira preparação L7 falhou no builder citado acima; após a correção, a preparação L7 e as preparações L3/L5 falharam por ausência do Chromium correspondente. As três repetições planejadas do cenário de atraso e a inspeção visual não foram executadas. O harness foi alterado, mas sua reprodução e a correção do defeito ainda não estão demonstradas por HTTP.

O HTML do pacote histórico reutilizava a captura L6-B anterior. Nesta integração foi gerada uma execução L6-B própria e uma cópia L7 em diretório de evidências fora do repositório; coleta e build concluíram com código zero. Isso não valida navegação nem aparência. Capturas anteriores não foram modificadas. Logs por suíte, versões, hashes do código testado e diffs separados estão em `EvidentGraph-L7-evidencias-20261019/`, ao lado do clone neste ambiente local.

As previsões permanecem condicionais e de autoria controlada; não houve avaliação externa, entrevistas, aprovação de segurança ou validação comercial. Os fontes M3, dataset original, L6-A/L6-B, equipe, dados pessoais e oportunidades não mudam. O histórico L4 pode recusar código de outra revisão conforme seu contrato; não se força compatibilidade nem se altera captura histórica.

## Reprodução e próximo ponto

Ver `review-ui/README.md`. Usar os requisitos fixados de Python/Playwright e uma plataforma suportada pelo navegador correspondente, com sandbox funcional. Não existe novo serviço em nuvem, importação de dados empresariais ou autenticação de produção.

Depois desta revisão, fechar o marco funcional com uma avaliação de tarefa por outra pessoa e uma decisão explícita sobre publicação isolada. Não ampliar novamente o parser por uma sequência indefinida de casos internos. A candidatura pode ser trabalhada após esse marco, conforme a orientação do proponente.

## Referências técnicas

- MDN, DOMContentLoaded: https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event — ordem de scripts defer e eventos.
- Playwright, Navigations / Hydration: https://playwright.dev/python/docs/navigations#hydration — controles visíveis antes da conexão dos ouvintes.

As referências orientam o diagnóstico, não comprovam os resultados locais nem a originalidade do produto.

## Entrega histórica de 2026-10-17

A tentativa de `GitHub.create_blob` foi bloqueada pelas configurações de segurança da ferramenta. Não houve SHA retornado, atualização da branch, comentário de PR, merge ou deploy. O trabalho L7 está somente nos arquivos locais e no patch entregue. PR #3 segue no head de base `09a1d42cce8506d0e7a801fd191914c4fdbfd142`. Nenhum resultado de CI novo é atribuído a esta entrega.

Além dos 249 testes Python, dez verificações offline por DOM passaram: grafo, lista, distinções de evidência, notas em sessão, referência posterior, casos semânticos, relatório filtrado, largura 1366, inicialização separada do Aurora e reprodução da perda de um ouvinte tardio. Não são testes de navegação HTTP ou persistência real entre recargas. O teste de carga atrasada por HTTP foi preparado, mas não executado nesta sessão.
