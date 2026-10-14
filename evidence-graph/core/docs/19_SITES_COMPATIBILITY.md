# Preparação para Codex / Sites — EvidentGraph

**Data:** 2026-10-14  
**Base conferida:** `fcb5592ce35887520ab8ab6e1d10a5d18586bb28`  
**Estado:** pacote estático preparado; Sites não provisionado nem validado.  
**Branch desta tarefa:** `chore/sites-readiness-20261014`.

## Resultado

A interface M3 do **Grupo Aurora** foi preservada. Os dez arquivos do pacote estático correspondem aos blobs da base publicada: HTML, CSS, JavaScript, dados e manifesto. Nenhum redesenho, alteração do analisador ou troca de endereço foi realizado.

A preparação adiciona um empacotador com lista explícita de arquivos, testes de integridade e uma tarefa para o Work/Codex com Sites. Não é migração concluída. Não foi criado um projeto Sites, salva uma versão Sites ou realizado deploy no Sites.

## O que o código atual requer

| Item observado no código | Implicação para a avaliação |
|---|---|
| HTML, CSS, JavaScript e SVG; caminhos relativos | Candidato a reaproveitamento como arquivos estáticos; a plataforma ainda deve aceitar os artefatos |
| `data.js` com gzip/base64 e `DecompressionStream('gzip')` | O navegador precisa decodificar os dados; não é cifragem nem backend |
| `localStorage` para notas/verificações | Dados pertencem à origem e ao navegador; não migram automaticamente do Pages para Sites |
| Downloads por `Blob` | Conferir download real no navegador/iframe do destino |
| Elementos `dialog`, eventos e manipulação do DOM | Conferir interação e política de execução no runtime de destino |
| Análises M1 pré-calculadas, com 240 ativos/512 relações | Manter resultados e limites; não inventar uma nova IA ou API |
| Python apenas na geração e testes | Não é necessário hospedar Python para exibir o pacote estático já gerado |

**Inferência de engenharia:** há poucos acoplamentos de hospedagem, portanto vale um teste de compatibilidade. Isso não prova suporte no Sites. Não adicionar React, banco, autenticação, Workers ou `.openai/hosting.json` fictício para apenas reproduzir esta interface.

## Procedimento reproduzível

Na raiz do repositório:

```sh
python evidence-graph/core/demo-ui/prepare_portable_preview.py --check
python -m unittest discover -s evidence-graph/core/demo-ui -p test_portable_preview.py -v
python evidence-graph/core/demo-ui/prepare_portable_preview.py --out /CAMINHO/NOVO/aurora-static
```

Use um diretório novo fora da pasta fonte. O script recusa sobrescrita, copia somente os dez arquivos permitidos, valida o hash do dataset e escreve `portability-report.json`. Não coleta credenciais, não usa rede e não publica. O relatório de portabilidade não é uma auditoria de segurança completa.

Para servir somente o pacote, em um terminal separado:

```sh
python -m http.server 8765 --bind 127.0.0.1 --directory /CAMINHO/NOVO/aurora-static
```

Teste HTTP opcional, com Playwright/Chromium instalados: configurar `EG_PREVIEW_URL=http://127.0.0.1:8765/` e executar `python evidence-graph/core/demo-ui/test_hosted_preview.py -v`. Não executar como evidência de sucesso se todos os testes forem pulados. Em um Sites privado, também será necessária uma sessão autenticada de revisão; o runner não contorna autenticação.

## Verificações executadas nesta etapa

- 43 testes do modelo M1: aprovados.
- 13 testes Node de exploração: aprovados.
- 20 testes Chromium da navegação M3, usando `set_content`: aprovados.
- 13 testes novos de empacotamento: aprovados.
- Total: **89 testes locais aprovados**, com escopos distintos. Não é uma execução de CI nem uma avaliação com usuários.
- Hash SHA-256 do dataset descomprimido: `08181b8b47836d0adf630c5430c5d6d9745fa6703127409904ebd8a1b1172e2b`.
- A cópia local prévia de gzip tinha um byte de identificação de sistema diferente. Foi recomposta a representação que coincide com o blob versionado de `data.js`; conteúdo descomprimido e manifesto são idênticos. Não houve alteração de dados.
- A tentativa de navegação HTTP local foi bloqueada com `ERR_BLOCKED_BY_ADMINISTRATOR`. Não foi contornada nem contada como teste aprovado. O runner `test_hosted_preview.py` foi preparado, mas seus seis testes HTTP ainda precisam de execução no ambiente de destino.

Ambiente local: Python 3.13.5, Node 22.16.0, Chromium via Playwright. A sintaxe do runner HTTP foi conferida; isso não substitui sua execução.

## O que ainda falta

1. Abrir o projeto no Work/Codex com o recurso nativo `@Sites` disponível.
2. Avaliar compatibilidade no runtime real, sem trocar a interface por uma nova.
3. Salvar uma versão para revisão, sem deploy nem alteração da audiência.
4. Conferir grafo/lista, downloads, teclado, notas após recarga e ausência de regressões visuais.
5. Registrar adaptações e resultados antes de decidir pela publicação.

A nova origem pode começar sem as notas do Pages. Isso é esperado e não autoriza importar dados pessoais nem adicionar armazenamento remoto silenciosamente. Não ampliar o escopo para migração do futuro backend ou coleta de dados reais.

## Documentação externa consultada

Fontes oficiais acessadas em 2026-10-14:

- OpenAI, **Sites**: https://learn.chatgpt.com/docs/sites — descreve projetos existentes compatíveis, avaliação de artefatos, versões salvas separadas do deploy e ausência de gestão Sites autônoma pela CLI.
- OpenAI Help, **Creating and using ChatGPT Sites**: https://help.openai.com/en/articles/20001339-creating-and-using-chatgpt-sites — orienta iniciar pelo Work na web ou Work/Codex no desktop e revisar antes de publicar.

Essas fontes descrevem o produto, não a disponibilidade na conta do proponente. Nesta conversa não há ação habilitada para criar ou salvar um Sites. A busca de ferramentas não encontrou um conector apropriado; não instalamos serviços alternativos.

**Próxima instrução:** [20_CODEX_SITES_TASK.md](./20_CODEX_SITES_TASK.md).
