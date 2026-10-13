# EvidentGraph — Grupo Aurora

Prévia com **grafo + lista de impacto + inventário**. Grupo Aurora é uma organização fictícia. Toda a base é sintética; a indicação foi concentrada em “Sobre o ambiente” para evitar repetição na interface.

## Abrir

O ZIP entregue já inclui `data.js`. Extraia tudo e abra `index.html` nesta pasta em um navegador recente.

Ao clonar a branch, gere os dados primeiro, a partir da raiz do repositório:

```sh
python evidence-graph/core/demo-ui/build_preview.py
```

Não precisa de servidor ou credenciais. As saídas regeneráveis `data.js` e `manifest.json` permanecem ignoradas no Git.

## Explorar

A abertura mostra o contexto da API de clientes. Clique em um ativo; use **Revisar impacto** ou **Lista** para consultar consumidores e ações. **Grafo** retorna ao mapa sem limpar filtros da análise. Em Escopo, escolha **Empresa inteira** para acessar o catálogo completo ou **Caminhos da análise** para o recorte da revisão. Há zoom, arraste, busca, filtro por área e expansão de conexões.

## Validação e limites

Veja [17_M2_GRAPH_REVIEW.md](../core/docs/17_M2_GRAPH_REVIEW.md). O mapa usa as 512 relações; análises de impacto permanecem limitadas aos três cenários preparados pelo analisador M1. Não há avaliação de autorização ou integrações de produção.

A branch segue em revisão no PR #1, sem substituir o site público.
