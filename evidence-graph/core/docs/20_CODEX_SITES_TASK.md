# Tarefa para Work / Codex com @Sites

## Mensagem pronta para iniciar

> @Sites, prepare uma versão de revisão do website EvidentGraph já existente; não crie outro design. Use o repositório ASCCJR/asccjr.github.io, branch `chore/sites-readiness-20261014`, e leia `evidence-graph/core/docs/19_SITES_COMPATIBILITY.md` e este arquivo. Reproduza `evidence-graph/preview-m2/` preservando Grupo Aurora, grafo/lineage como entrada, lista sincronizada, investigação por ativo, filtros, notas e exportação. Verifique a compatibilidade e teste a experiência. Salve uma versão para revisão, sem fazer deploy ou alterar o GitHub Pages. Antes de mudar framework, armazenamento ou arquitetura, apresente a necessidade e aguarde aprovação.

## Base e continuidade

Base M3 conferida: `fcb5592ce35887520ab8ab6e1d10a5d18586bb28`. O PR de preparação não altera a UI. Atualize a branch local a partir do remoto antes de trabalhar; não recrie uma branch divergente nem sobrescreva trabalho alheio.

Ler `18_ASSET_INVESTIGATION.md` e `17_M2_GRAPH_REVIEW.md` para a decisão de manter o grafo. A diretriz antiga de começar apenas pela lista não prevalece sobre essa revisão.

Se receber o ZIP de preparação em vez do repositório, `site/` contém os dez arquivos originais e o relatório de hashes. As alterações continuam devendo ser reconciliadas com o repositório, não tratadas como produto paralelo.

## Invariantes

- Manter Grupo Aurora, cores, layout e funcionalidades. Não remover o grafo.
- Preservar 240 ativos, 512 relações, três cenários, dataset e limites do analisador.
- Sobre o ambiente e relatórios explicam dados fictícios; não espalhar “demo” pela navegação.
- Não acrescentar login, banco, LLM, dados de empresa, currículo ou contatos pessoais.
- Não alterar os arquivos antigos em `evidence-graph/index.html`, `app.js` e `styles.css`, nem a variante Claro ou materiais acadêmicos.
- Não recriar `index.html` na raiz do repositório; raiz do pacote de publicação não é raiz do repositório.
- Não criar IDs/URLs/manifestos de Sites fictícios. Não declarar sucesso sem uma versão salva realmente retornada pela ferramenta.
- Sites não é requisito para o backend futuro; esta tarefa é somente uma experiência de prévia.

## Executar

1. Conferir o recurso Sites. Se ausente, informar exatamente a limitação; não substituir por um plugin de hospedagem genérico.
2. Executar `prepare_portable_preview.py --check` e os testes descritos em `19_SITES_COMPATIBILITY.md`.
3. Importar/adaptar os arquivos estáticos apenas no necessário. Apresentar qualquer adaptação antes de alterar arquitetura.
4. Conferir uma URL de prévia real quando disponível. Testes com DOM injetado não comprovam hospedagem.
5. Verificar: API de clientes → Quem depende dele? → Até 2 níveis → Grafo/Lista → Agente de atendimento → Revisar consumidor → nota → exportação → recarga → nota preservada na mesma origem.
6. Repetir: dashboard de reposição → De que depende?; CHG-003 deve continuar inconclusivo.
7. Conferir 1366×768 e 1920×1080, teclado, erros de console, arquivos carregados e downloads. Testar zoom real, sem confundir redução da viewport com zoom do navegador.
8. Salvar uma versão Sites, sem deploy. Documentar ID real, commit-fonte e resultados; não alterar audiência, DNS ou URL atual.
9. Entregar diff mínimo, prévia revisável, testes aprovados/falhos/bloqueados e recomendação de seguir com Sites ou manter Pages.

As notas do Pages não aparecerão automaticamente em outra origem. Não prometer sincronização ou migrar notas para armazenamento remoto sem decisão explícita.

## Conclusão da tarefa

Concluída apenas quando a experiência existente estiver reproduzida e revisável no Sites com as limitações documentadas. Empacotar arquivos, abrir PR ou testar localmente são etapas úteis, mas não equivalem a criar um Sites.
