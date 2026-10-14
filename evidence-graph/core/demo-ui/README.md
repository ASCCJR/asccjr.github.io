# Build e testes de interface M2

`build_preview.py` usa o modelo M1 sem modificá-lo, calcula os três resultados e gera `../../preview-m2/data.js` e `manifest.json` de forma determinística. Essas saídas são regeneráveis e não ficam no Git. O ZIP entregue na conversa já as inclui.

`test_ui.py` executa 18 testes de DOM em Chromium via Playwright. Como a navegação local foi bloqueada no ambiente utilizado, os arquivos locais são inseridos diretamente na página de teste. Nenhuma rede externa é usada. O fallback sem armazenamento persistente é exercitado; não se trata de teste de publicação.

```sh
python build_preview.py
python -m unittest -v test_ui
```

Informe `CHROMIUM_PATH` quando Chromium não estiver em `/usr/bin/chromium`. Playwright é uma dependência apenas de teste. Os resultados da verificação estão em `../docs/16_M2_PREVIEW.md`.
