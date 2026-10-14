# M2 — Prévia funcional de revisão de mudanças

**Data:** 2026-10-13  
**Status:** implementada em branch de revisão; sem merge ou publicação; não substitui a demonstração anterior.  
**Entrada local após build:** [prévia](../../preview-m2/index.html).

## Entrega

Interface em português para selecionar uma das três mudanças preparadas, abrir o resultado, filtrar consumidores por conclusão, responsável, atividade e texto, ordenar por nome, examinar caminhos e evidências, anotar verificações e exportar o recorte em Markdown.

O inventário permite pesquisar e paginar os 240 ativos sintéticos. Não há mapa empresarial nesta etapa. O painel de um ativo sem cenário preparado informa essa limitação, sem sugerir ausência de dependências.

Os resultados continuam sendo os produzidos pelo analisador Python M1. A interface **não recalcula** contratos arbitrários: carrega resultados de referência gerados durante o build. Mudanças nas evidências exigem regeneração. O bundle inclui o inventário completo, mas somente 8 relações e 17 evidências pertinentes aos cenários. Não é uma implementação de consulta geral das 512 relações.

## Verificação executada

- Conferidos os hashes Git dos arquivos model.py e test_model.py: iguais aos da main na revisão M1.
- 43 testes da base M1 passaram novamente.
- 18 testes M2 passaram em Chromium local com Playwright: cenários, seleção pendente, filtros, ordenação, evidências, foco de retorno, notas, exportação de arquivo Markdown, inventário, paginação, referências e escape de HTML.
- Inspeção visual das telas de análise, detalhe e inventário; renderização em 1366×768, 1440×1000 e 1920×1080; teste adicional de reflow em 683×384.
- O navegador deste ambiente bloqueou navegação por file:// e HTTP local. Para executar os testes, HTML/CSS/JS locais foram inseridos no DOM com Playwright, sem requisições externas. Isso testa a interface, não a publicação no GitHub Pages.
- localStorage não está disponível nessa origem isolada: foi testado o fallback em memória da sessão. Persistência após recarga em origem publicada e zoom real de navegador a 200% ainda precisam de verificação.

Esses testes não são sessões com usuários nem avaliação em produção. Aprovação visual do proponente e discovery continuam pendentes.

## Reprodução

```sh
cd evidence-graph/core/demo-data
python -m unittest -v test_model
cd ../demo-ui
python build_preview.py
python -m unittest -v test_ui
```

O build usa apenas a biblioteca padrão do Python. Os testes de interface precisam de Playwright e Chromium; o caminho pode ser informado em `CHROMIUM_PATH`. A prévia usa a API nativa DecompressionStream para ler um pacote gzip local; não há biblioteca de terceiros nem serviço externo em runtime.

Os arquivos gerados data.js e manifest.json ficam fora do Git e são reproduzidos pelo build. O ZIP entregue na conversa já os inclui; clonar a branch exige executar o build antes de abrir a interface.

## Privacidade e continuidade

Não há envio de dados, autenticação real, mensagens a responsáveis, aprovação de mudança ou bloqueio de deploy. Notas e checkboxes são anotações locais, não comprovação de correção do impacto. Nenhum currículo, identidade pessoal ou arquivo da Claro foi alterado nesta etapa.

O site anterior em `evidence-graph/index.html` permanece intacto. Próximo marco: exploração contextual do grafo maior, alinhada à jornada, e avaliação de UX. Não afirmar que a interface já reconcilia fontes de produção ou avalia IAM.
