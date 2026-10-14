# EvidentGraph — Grupo Aurora

Versão de avaliação com grafo, lista, investigação por ativo e análise de mudanças. O Grupo Aurora e seus dados são fictícios. Site de avaliação: `/evidence-graph/preview-m2/`; a versão anterior em `/evidence-graph/` permanece preservada.

## Abrir

Depois de gerados/versionados os dados, abrir `index.html` ou o endereço do GitHub Pages. Não há backend ou credenciais. Para regenerar:

```sh
python3 evidence-graph/core/demo-ui/build_preview.py
```

## Funcionalidades

Selecionar um ativo; investigar dependências, consumidores ou processos; variar alcance; alternar grafo/lista sem trocar o contexto; revisar um consumidor nos cenários existentes; registrar verificações e exportar Markdown.

`exploration.js` contém as regras de alcance tipado; `investigation.js` mantém contexto/seleção compartilhados e exporta o recorte. `lineage.js` desenha o mapa. `app.js` mantém análises pré-calculadas pelo Python M1, inventário e notas locais.

## Testes

```sh
cd evidence-graph/core/demo-data && python3 -m unittest -q test_model
cd ../demo-ui && node --test test_exploration.cjs
python3 -m unittest -q test_navigation
```

O último comando requer Playwright e Chromium. Consulte `../core/docs/18_ASSET_INVESTIGATION.md` para escopo, evidência de teste e limitações. Os testes de UI nesta etapa usam DOM local, não validação de implantação.
