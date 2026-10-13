# Revisão da M2 — grafo e análise complementares

**Data:** 2026-10-13. **Estado:** prévia de revisão na branch do PR #1, sem merge.

## Feedback e correção

O proponente considerou exagerada a remoção do lineage visual, embora reconheça a utilidade da lista operacional. Pediu para preservar o apelo visual do grafo e retirar a repetição de “demo” na interface.

A decisão é complementar, não substituir: o mapa volta como entrada, com acesso à lista de impactos, inventário, evidências e exportação. Esta correção qualifica a direção task-first: responder perguntas não exige esconder o grafo ou removê-lo de uma entrega intermediária.

## Implementado nesta revisão

- Organização fictícia **Grupo Aurora**, sem associação a uma empresa real.
- Nomes de equipe e ambiente apresentados sem “Demo”; origem sintética descrita em **Sobre o ambiente** e nos relatórios exportados.
- Grafo SVG com relações direcionadas, seleção, zoom, pan, foco e expansão de vizinhança.
- Recorte inicial: 27 ativos e 46 relações do entorno da API de clientes.
- Modo **Empresa inteira**: 240 ativos e 512 relações; também há filtro por área e opção de colunas/identidades.
- Grafo e lista compartilham a mudança selecionada. Voltar à lista não limpa seus filtros; o modo “Caminhos da análise” respeita o filtro de consumidores.
- Nó abre responsável, processo, conclusão quando disponível e evidências. Relações também permitem examinar evidências.
- Inventário leva à vizinhança de qualquer ativo, sem prometer análise de impacto universal.

## Testes executados

43 testes da base M1 passaram novamente. 20 testes adicionais da revisão passaram em Chromium/Playwright: abertura pelo grafo, 240 nós/512 relações, contagens do recorte, nomes, aviso em Sobre, seleção de caminho, detalhes, zoom, busca, cenários sincronizados, preservação de filtros, domínio, inventário, expansão, relatório, teclado, largura 1366, incerteza e proveniência de relações.

A navegação `file://` é bloqueada neste ambiente de teste. Por isso HTML, CSS e JavaScript foram carregados diretamente no DOM. Isso não valida o comportamento do ZIP extraído em todos os navegadores nem a persistência em uma origem publicada. Inspeção visual realizada em 1920 e 1366 pixels. Código publicado conferido por hashes de blobs com os arquivos locais testados.

## Limitações preservadas

As análises de impacto continuam pré-calculadas pelo Python M1, limitadas aos três cenários. O mapa usa o catálogo completo, mas linhas adicionais não comprovam impacto, execução ou permissão. Não há avaliação IAM, bloqueio, integração real nem validação com clientes.

O layout em colunas é inicial: em visão completa o usuário precisa filtrar ou ampliar. Não foi implementado um motor de layout comercial. Os testes anteriores de M2 documentam a versão anterior; `test_graph.py` cobre a navegação revisada.

O site público anterior, o Core técnico, a variante Claro, arquivos acadêmicos e integrantes não foram alterados nesta revisão.
