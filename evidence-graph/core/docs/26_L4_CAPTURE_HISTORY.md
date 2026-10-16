# L4 — novas capturas, histórico e comparação local

**Data:** 2026-10-16. **Base:** PR #3, revisão `4c8e402c3c68744c16b6e9b2bcc6bd7bd9174bee`.  
**Estado:** implementação local, na branch do laboratório; sem merge ou publicação.  
**Direção:** continuar o Core do ponto em que estava. A candidatura CTE-IA é uma frente separada, não requisito para esta implementação. Não foi introduzida IA artificialmente para atender ao edital.

## Entrega

`lab-runtime/capture_history.py` reúne execução L1, validação, análise e preparação do viewer L3 em um comando. Cada captura recebe uma pasta exclusiva, dados de origem, relatórios, manifesto de integridade e HTML próprio. O comando não modifica os arquivos de apresentação em `preview-m2/`, não atualiza Pages e não une Aurora Lab ao catálogo Grupo Aurora.

Sem ID informado, o programa gera um identificador por data UTC e componente aleatório. Um ID repetido é recusado. `capture.json` é gravado ao fim: uma pasta interrompida não é listada como concluída. Os resultados ficam em arquivos locais, não são commits Git por captura. Não é armazenamento imutável contra administradores ou autenticação criptográfica de origem.

## Comandos

Com as dependências já descritas em `lab-runtime/requirements.txt`, na raiz do repositório:

```sh
python evidence-graph/core/lab-runtime/capture_history.py capture --id coleta-01
python evidence-graph/core/lab-runtime/capture_history.py capture --id coleta-02
python evidence-graph/core/lab-runtime/capture_history.py list
python evidence-graph/core/lab-runtime/capture_history.py compare coleta-01 coleta-02 --out evidence-graph/core/lab-runtime/runs/comparacao-01-02
```

O arquivo de visualização de cada execução fica em `core/lab-runtime/runs/captures/<ID>/view/EvidentGraph_L2.html`. O nome interno do viewer foi preservado; seu conteúdo usa a nova captura. Não é necessário remontar a interface manualmente. Para repetir o comando, usar outro ID e outra pasta de comparação.

`--archive` permite escolher outra pasta de histórico; deve aparecer antes do subcomando. O programa recusa diretórios não vazios sem marcador reconhecido, symlinks e escrita nos fontes do projeto. Dentro de `evidence-graph/`, as saídas devem ficar em `lab-runtime/runs/`.

## Integridade e comparação

A leitura confere os hashes de todos os artefatos registrados, inclusive visualização, e recalcula o resultado a partir de `run.json`. Edição isolada de uma conclusão em cache não vira nova evidência. Arquivos faltantes, adicionais ou alterados invalidam a captura. Alteração do código registrado exige usar a revisão correspondente; não há reinterpretação silenciosa com outra versão do analisador.

A comparação aceita o cenário delimitado L1, com os mesmos consumidores, rota, esquema, transporte e rótulos de versão. Recusa a mesma captura apresentada como duas execuções, ordem temporal invertida e intervalos sobrepostos. A identidade do ambiente é a convenção do laboratório L1, não descoberta automática de infraestrutura empresarial.

Compara contrato, campos removidos exigidos, uso anterior, verificação posterior e estado de autorização. Também informa diferenças nos documentos OpenAPI e nas declarações. IDs e tempos novos não são anunciados como mudança de risco. Perda de observação continua sendo desconhecimento, não ausência de dependência.

## Execução de referência desta etapa

Duas novas execuções de laboratório ocorreram por HTTP loopback real:

| Captura | Intervalo UTC | Spans / traces |
|---|---|---|
| execucao-01 | 2026-10-16T16:28:33.868112+00:00 a 16:28:34.305733+00:00 | 12 / 4 |
| execucao-02 | 2026-10-16T16:28:35.605078+00:00 a 16:28:36.055916+00:00 | 12 / 4 |

SHA-256 dos respectivos `run.json`:

```text
da65749b31af97d9cb722c84d71a22e483cb3f7c60e2d2bb1f86893fea2fe5e8
0e3945eeb6e544f87568ef49601855110a48ad2bf2c44bfce13df544ad642fa6
```

A comparação produziu **zero consumidores com mudança de conclusão**: o cenário executado foi o mesmo, embora os traces e os hashes sejam distintos. Pedidos falha no teste de remoção de campo, Portal passa na verificação executada e Exportador permanece não verificado. Não foi inventada uma melhoria entre duas execuções equivalentes.

## Testes

**76 testes locais aprovados nesta rodada:** 28 L1, 24 adaptador e 24 novos de histórico. Comando:

```sh
cd evidence-graph/core/lab-runtime
python -m unittest -v test_lab test_adapter test_capture_history
```

Os testes de referência fazem duas execuções reais; mocks aparecem somente em testes de falha, incompatibilidade de contexto e perda de observação. Foram verificadas preservação, recusa de sobrescrita, integridade, correspondência captura/viewer, comparação e desconhecimento. Os dois fontes novos enviados foram conferidos por SHA de blob com os executados.

Não houve nova rodada de navegador ou validação com usuários. O sucesso HTTP registrado na L3 pertence àquela revisão; não deve ser somado como novos testes desta etapa. A suíte L4 foi executada localmente, não se afirma execução dela no CI.

## Limites e retomada

A aplicação visual não foi redesenhada. O histórico e sua comparação estão disponíveis por comando e relatório Markdown/JSON; ainda não existe um seletor gráfico entre várias capturas nem atualização contínua. Cada HTML continua uma fotografia histórica. As notas seguem a separação por fonte/hash já implementada na L3; não são migradas automaticamente entre execuções.

Os dois conjuntos permanecem separados: captura local pequena e catálogo sintético maior. Sem novos conectores, IAM, MCP, LLM, benchmark independente ou sistema de produção. O comparador continua apoiado nos requisitos declarados do laboratório.

**Próximo ponto técnico:** revisão deste fluxo de histórico; depois L5, autorização local explícita com casos permitido, negado e indeterminado. A publicação continua dependendo de decisão própria. O edital é acompanhado separadamente e não redefine automaticamente essas prioridades. Ver também [24_CORE_NEXT_STEPS.md](./24_CORE_NEXT_STEPS.md).
