# L7 — níveis de evidência na experiência existente

## Estado atual — Checkpoint 3 concluído, 2026-10-19

**L7 pronta para revisão de merge; publicação não autorizada.** PR [#3](https://github.com/ASCCJR/asccjr.github.io/pull/3) permanece rascunho, na branch `feat/core-runtime-lab-20261015`. As seções históricas abaixo descrevem seus respectivos momentos, inclusive bloqueios e falhas; o resultado atual é o desta seção.

### Código e ambiente efetivamente testados

HEAD de código/workflows: `1a1324c56694474dcf76a16466c0c22693d808a9`. Checkout real dos três runs: `3f07940e795ec69561e69a57116b5b241dde16e0`, merge temporário com pais `fcb5592ce35887520ab8ab6e1d10a5d18586bb28` (`main`) e o HEAD acima. Os objetos foram comparados: as árvores de arquivos são idênticas. As asserções de identidade foram mantidas nos dois jobs de navegador.

Somente os dois jobs de navegador passaram de Ubuntu 24.04 para Ubuntu 22.04. Runner confirmado: Ubuntu 22.04.5 LTS, Python 3.12.15, Playwright 1.57.0, Chromium 143.0.7499.4, revisão 1200, usuário UID 1001. O lançamento headless usa o headless shell correspondente instalado pelo Playwright, sem override de executável e com `chromium_sandbox=True`. As linhas reais de lançamento não contêm `--no-sandbox`; nenhuma política de AppArmor, seccomp ou sysctl foi desabilitada. Requisitos declarados não mudaram.

Antes das suítes, ambos os jobs iniciaram o navegador, receberam HTTP 200 em `127.0.0.1`, clicaram em um botão JavaScript (contador 0 → 1), não registraram erro de página e encerraram navegador/contexto/servidor. A verificação registra versões/opções e tem contagem funcional zero; não constitui auditoria completa de segurança. Se ela falhar, as suítes não rodam e só há diagnóstico de leitura. Após sua aprovação, cada job conserva os códigos Python/tee, tenta todas as suas suítes e termina em falha se alguma falhar, sem `continue-on-error`.

### Resultados confirmados

| Run / job | Python | HTTP e repetições | Resultado |
| --- | --- | --- | --- |
| [39335649585](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39335649585) / 118344371296 | 124 laboratório + 43 L6-A + 62 L6-B | — | Aprovado |
| [39335649610](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39335649610) / 118344371534 | 124 laboratório, repetidos | 12 `test_browser_http` + 10 `test_auth_browser` | Aprovado |
| [39335649617](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39335649617) / 118344371616 | 20 L7 | 14 `test_review_http` + três repetições adicionais de `test_02` | Aprovado |

São **249 testes Python e 36 casos HTTP distintos**, sem falhas, erros ou skips nesses runs. Os 124 repetidos não ampliam o total Python; as três repetições não criam novos casos HTTP. Os mesmos 249 casos Python também passaram localmente antes do commit, com hashes dos arquivos preservados; isso não aumenta a contagem. As falhas anteriores não foram apagadas nem substituídas por uma simples reexecução.

O controle antigo reteve a resposta HTTP de `auth_view.js` até observar `eg:ready` uma vez e seis nós de grafo. Após liberar a extensão, selecionar `aurora` deixou URL em `access` e dados em `l5_capture`: o ouvinte tardio havia perdido o evento. Na versão corrigida, com a resposta ainda retida, `EGStart` estava definido, o seletor desabilitado e a contagem de prontidão em zero. A liberação iniciou corretamente; quatro trocas Aurora/Acesso conservaram 240/10 ativos e um único evento por documento. Isso passou na suíte e nas três repetições adicionais. A fixture reproduz e detecta esse defeito de inicialização; não comprova que ele causou o timeout histórico de L6-B.

### Inspeção visual e funcional

As **12 PNG reais do run 39335649617 foram abertas e examinadas**, além da leitura dos logs e dos dois relatórios exportados. Asserções HTTP confirmaram troca das três fontes, grafo/lista com os mesmos IDs, voltar/avançar/recarregar, notas isoladas por fonte e entre duas capturas L7, separação de níveis, exportação filtrada e Aurora completo. As 17 observações de encerramento L7 (14 casos e três repetições) têm `page_errors=[]` e `console_errors=[]`; as duas suítes anteriores também passaram suas asserções de erro de página e ausência de pedidos HTTP externos.

| Imagens | Avaliação da inspeção |
| --- | --- |
| `review-graph.png`, `review-list.png` | Mesma fonte/foco, contagem 13/12 e painel de contexto; controles, lista e grafo mantêm o visual existente. Rótulos longos do grafo ficam abreviados; lista/painel mostram o contexto. |
| `c06-levels.png`, `c10-unknown-tested.png` | Três níveis separados; c06 mostra leitura observada sem prever exceção; c10 conserva inferência inconclusiva mesmo exibindo exceção no teste histórico. |
| `n01-business.png`, `n02-business.png` | Ambos concluem sem exceção; n01 exibe requisito violado e n02 atendido, com requisito e referência de teste em seção própria. |
| `filtered-export.png` | Busca por Pedido identificado deixa 1 de 8 consumidores; os conteúdos Markdown com/sem histórico foram lidos no log e preservam essa seleção. |
| `aurora-complete.png`, `source-history.png` | Aurora exibe 240 ativos/512 relações; Validação após avançar exibe 9/8. O ajuste do grafo inteiro fica em 16% e não permite ler todos os rótulos nessa visão; zoom/lista continuam disponíveis. |
| `notes-source.png`, `notes-capture-a.png`, `notes-capture-b.png` | Layout do painel consistente. Limite dessas capturas: o campo de nota fica abaixo da parte visível do painel com rolagem; as PNG não demonstram o texto da nota. Persistência/isolamento foram confirmados pelas asserções reais de leitura do campo nos casos 07 e 14. |

A inspeção não encontrou regressão visual impeditiva no recorte de 1366 px; não é avaliação externa de usabilidade, responsividade completa ou prova de ausência de defeitos. Screenshots de página inteira mostram painéis fixos apenas na região correspondente ao viewport, não todo o conteúdo de rolagem interna.

### Histórico preservado e limites de continuidade

- WSL local Ubuntu 26.04 continua incompatível com a instalação fixada: o registro oficial não fornece o download para `ubuntu26.04-x64`. Nenhuma alteração local de plataforma, Docker, navegador alternativo ou proteção foi feita.
- Runs iniciais `39333069823`/`39333071063`: contexto `runner.temp` em posição inválida; corrigido para o passo. Runs `39333339596`/`39333339724`: leitura de pais vazia em checkout raso; corrigida pela leitura do objeto bruto, mantendo as asserções.
- Ubuntu 24.04, HEAD `ef143550c486529adadb7e41ee07c80c079ea701`: revisão [39333611202](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39333611202) e laboratório [39333611188](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39333611188) falharam com `No usable sandbox!` antes de executar casos HTTP. Autorização e repetições foram impedidas pelo passo anterior; zero screenshots. O erro é confirmado, mas a política específica do host não foi isolada. Avaliação `39333611182` passou as 229 regressões Python.
- Nesta continuação em Ubuntu 22.04, não houve falha funcional nem alteração dos oráculos, heurísticas ou do código do produto. O diff é dos dois workflows e do verificador preliminar, seguido apenas por documentação de continuidade.
- Artefatos selecionados: 27 arquivos (15 logs + 12 PNG), sem viewer ou capturas completas; retenção GitHub de sete dias. Revisão de padrões de credenciais sem achados, sem alegar auditoria exaustiva. Evidências locais necessárias: `EvidentGraph-L7-evidencias-20261019/etapa3-ubuntu22/`, fora do clone. Artefatos remotos são temporários.
- Alterações posteriores ao HEAD testado limitam-se a `00_START_HERE.md`, este checkpoint e `review-ui/README.md`; nenhuma mudança posterior em código/workflows. `main` continua `fcb5592ce35887520ab8ab6e1d10a5d18586bb28`; Pages usa `main` `/`, com último build em 2026-10-14. Experimentos L6-A/B, resultados/capturas anteriores, dados Aurora e arquivos publicados não mudaram.
- Pendentes: revisão humana do PR, avaliação independente de tarefas/casos e decisão expressa do responsável sobre merge/publicação. O bloqueio local do navegador permanece. Este fechamento não autoriza trabalho de produto adicional.

## Registro da integração anterior ao fechamento

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

### Registro da primeira configuração no GitHub Actions (Ubuntu 24.04) — 2026-10-19

O diagnóstico local foi confirmado contra a distribuição oficial `playwright-core@1.57.0`: os bytes de `hostPlatform.js`, `registry/index.js` e `browsers.json` instalados conferem com ela. O detector retorna `ubuntu26.04-x64` e o registro tem zero URLs para esse Chromium; a exceção ocorre antes do aviso de fallback e da tentativa de download. Não foi uma falha de rede, biblioteca de sistema, política ou inicialização. As falhas posteriores de launch decorrem da ausência do executável. Não houve nova tentativa local de instalação, atualização de versão ou override da plataforma.

Os jobs de navegador de revisão e laboratório usam explicitamente Ubuntu 24.04, Python 3.12, Playwright 1.57.0 e seu Chromium, com dependências instaladas apenas no runner efêmero. O sandbox permanece exigido. Os logs registram o HEAD do PR, o SHA realmente obtido por checkout e seus pais, incluindo quando o GitHub testa um merge temporário. O cenário corrigido de extensão atrasada é repetido três vezes; repetições não ampliam a contagem de testes distintos.

O workflow de revisão seleciona apenas logs dos testes fictícios e screenshots para artefatos com retenção de sete dias; não publica o viewer, capturas completas ou dados pessoais. O workflow de laboratório conserva apenas seus logs selecionados. A configuração usa permissões de leitura e não altera Pages. Resultados precisam ser conferidos no run correspondente ao código final; esta seção descreve o mecanismo, sem certificar uma execução. Sucesso no runner não resolve a indisponibilidade do navegador no WSL local.

Referências da versão diagnosticada: [detecção de plataforma v1.57.0](https://github.com/microsoft/playwright/blob/v1.57.0/packages/playwright-core/src/server/utils/hostPlatform.ts) e [seleção de download v1.57.0](https://github.com/microsoft/playwright/blob/v1.57.0/packages/playwright-core/src/server/registry/index.ts).

Depois desta revisão, fechar o marco funcional com uma avaliação de tarefa por outra pessoa e uma decisão explícita sobre publicação isolada. Não ampliar novamente o parser por uma sequência indefinida de casos internos. A candidatura pode ser trabalhada após esse marco, conforme a orientação do proponente.

## Referências técnicas

- MDN, DOMContentLoaded: https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event — ordem de scripts defer e eventos.
- Playwright, Navigations / Hydration: https://playwright.dev/python/docs/navigations#hydration — controles visíveis antes da conexão dos ouvintes.

As referências orientam o diagnóstico, não comprovam os resultados locais nem a originalidade do produto.

## Entrega histórica de 2026-10-17

A tentativa de `GitHub.create_blob` foi bloqueada pelas configurações de segurança da ferramenta. Não houve SHA retornado, atualização da branch, comentário de PR, merge ou deploy. O trabalho L7 está somente nos arquivos locais e no patch entregue. PR #3 segue no head de base `09a1d42cce8506d0e7a801fd191914c4fdbfd142`. Nenhum resultado de CI novo é atribuído a esta entrega.

Além dos 249 testes Python, dez verificações offline por DOM passaram: grafo, lista, distinções de evidência, notas em sessão, referência posterior, casos semânticos, relatório filtrado, largura 1366, inicialização separada do Aurora e reprodução da perda de um ouvinte tardio. Não são testes de navegação HTTP ou persistência real entre recargas. O teste de carga atrasada por HTTP foi preparado, mas não executado nesta sessão.
