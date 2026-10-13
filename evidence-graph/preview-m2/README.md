# EvidentGraph — Prévia M2

Interface estática para revisão de mudanças, separada da demonstração anterior. Esta entrega está em uma branch de revisão, sem merge nem publicação no GitHub Pages.

## Abrir a partir do repositório

Gere primeiro os dados locais:

```sh
python evidence-graph/core/demo-ui/build_preview.py
```

Depois abra `index.html` nesta pasta, mantendo CSS, JavaScript e data.js juntos. Também pode servir a pasta por HTTP. O ZIP entregue na conversa já contém os dados gerados. Use navegador moderno com DecompressionStream.

## Como experimentar

1. Abra CHG-001 e veja os quatro consumidores com conclusões diferentes.
2. Filtre por impacto, equipe, atividade ou texto; limpe para restaurar.
3. Abra Detalhes, examine caminhos e evidências e adicione uma nota local.
4. Exporte a análise em Markdown: inclui apenas consumidores filtrados e suas notas.
5. Use Inventário para pesquisar os 240 ativos; há análises preparadas apenas para três cenários.

Resultados pré-calculados pelo analisador M1, não por LLM nem por um backend de produção. O navegador filtra e apresenta esses resultados.

`data.js` contém JSON comprimido em gzip/base64 para distribuição local. Não é criptografia nem proteção de dados. O gerador e o modelo de origem estão versionados. Não há dados reais.

Ver [validação M2](../core/docs/16_M2_PREVIEW.md). A navegação de grafo empresarial e a avaliação de permissões são etapas posteriores.
