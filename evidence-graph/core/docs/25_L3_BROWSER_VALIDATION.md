# L3 — estabilização e validação em navegador

**Data:** 2026-10-16. **Base revisada:** `64b360045351d6ed45207990e1e267366fea349a`, PR #3.

## Alterações implementadas

- Seleção de origem por parâmetro `source`, separada das âncoras da página; compatibilidade com o link legado `#aurora`.
- Uma navegação por troca de origem, em vez de alterar hash e recarregar separadamente.
- Aviso de notas temporárias quando o armazenamento não está disponível e confirmação antes de trocar de fonte nessas condições.
- Preservação de chaves distintas por dataset/captura, grafo/lista, análises, layout e arquivos M3.
- Suíte `test_browser_http.py` com 12 casos e workflow de CI com permissão somente de leitura, sem publicar nem fazer commits.

O ajuste é feito no builder/overlay do laboratório. Nenhum HTML/CSS/JS publicado em `preview-m2/` é modificado. O nome de saída `EvidentGraph_L2.html` permanece por compatibilidade; o pacote desta rodada pode renomear sua cópia para L3.

## Evidência local desta rodada

66 testes executados e aprovados: 28 do laboratório, 24 do adaptador e 14 da apresentação por DOM. Python 3.13; Playwright 1.57.0 com Chromium disponível no ambiente. Os testes executaram novos HTTP/SQLite locais e spans reais do laboratório para as suas próprias fixtures.

A tentativa de navegação HTTP do navegador gerenciado retornou `ERR_BLOCKED_BY_ADMINISTRATOR`. Não foi contornada, repetida com outro mecanismo nem contada como sucesso. A suíte HTTP teve sua sintaxe verificada localmente; os testes DOM não substituem os 12 casos HTTP. Não foram reexecutadas nesta rodada todas as suítes históricas M1/M3.

## CI — verificar execução, não presumir

O workflow `.github/workflows/evidentgraph-runtime-lab.yml` executa, no runner do GitHub, os 52 testes de laboratório/adaptador e os 12 de navegador por HTTP. A página é servida em loopback dentro do runner. Não utiliza `set_content` ou interceptação da navegação como fallback. O caso de armazenamento indisponível injeta explicitamente uma falha de escrita, apenas para avaliar esse comportamento.

O workflow somente lê o repositório, instala dependências e executa testes. Não usa credenciais de empresas, não publica capturas e não altera Pages. Um arquivo de workflow existente não comprova que executou. Consultar o status e os logs do PR #3 para o SHA revisado. Em caso de falha, mantê-la visível e corrigir antes de publicação.

## Reprodução

```sh
python -m pip install -r evidence-graph/core/lab-runtime/requirements.txt -r evidence-graph/core/lab-runtime/requirements-browser.txt
python -m playwright install chromium
cd evidence-graph/core/lab-runtime
python -m unittest -v test_lab test_adapter test_browser_http
```

A suíte cria capturas novas e duas visualizações temporárias, abre um servidor em `127.0.0.1` e o encerra ao concluir. Sem fallback de rede ou exigência de empresa conectada. O caminho `EG_BROWSER_PATH` pode selecionar um Chromium já instalado em um ambiente que permita executar o teste; não altera políticas do navegador.

## Escopo de comprovação

Sucesso no runner comprova o comportamento exercitado naquela origem HTTP e navegador. Não comprova implantação no GitHub Pages, todos os navegadores, dispositivo móvel, reinício completo do computador ou sincronização entre dispositivos. Abertura por `file://` continua útil para visualizar, mas a persistência nesse esquema não é portável; para avaliar armazenamento, usar uma origem HTTP estável.

A captura usada no HTML entregue é a mesma referência L2, preservada: `f4bb00c68fd5ddf9ddd04c6681befa96c3c71e9ecfdfc80c4695b6f81ae9b7f4`. Não foi rotulada como captura nova ou ao vivo. Testes geram suas próprias capturas descartáveis.

## Referências técnicas

- Playwright, navegação e espera por URL: https://playwright.dev/python/docs/navigations
- MDN, localStorage e limites de origem/file: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

## Continuidade

Concluir a avaliação HTTP, revisar com o proponente e decidir publicação isolada. Depois seguir [24_CORE_NEXT_STEPS.md](./24_CORE_NEXT_STEPS.md): novas capturas reproduzíveis, autorização/ferramenta local, avaliação independente e piloto. Discovery com usuários ocorre em paralelo. Sem merge ou deploy automático nesta rodada.
