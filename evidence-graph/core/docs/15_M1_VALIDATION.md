# EvidentGraph — Registro de validação do marco M1

**Data:** 2026-10-13 · **Execução:** local, Python 3.13.5, biblioteca padrão.  
**Escopo:** dados sintéticos, integridade e comportamento do analisador de referência.  
**Resultado:** 43 testes passaram. Não é execução de CI do GitHub nem teste em produção.

## Evidências produzidas

- Ativos: **240**; relações: **512**.
- Registros de evidência: **521**; registros de cobertura: **7**.
- CHG-001: quatro consumidores, três com caminho observado, um com cobertura insuficiente.
- CHG-002: dois consumidores; uma incompatibilidade de contrato e um impacto possível.
- CHG-003: um consumidor mensal; resultado inconclusivo, sem conclusão de segurança.
- Geração idêntica em chamadas repetidas, verificada por comparação dos bytes JSON.

SHA-256 de `enterprise.json`, gerado por `model.py`:

```text
ad90fedd8067abf115295d6201b7070a794464436f1d28a2378cd38e4491bcb8
```

## Comandos executados

```sh
python -m unittest -v test_model
python model.py --out build
```

A suíte cobre os oráculos independentes, contagens, vínculos intermediários, exclusão de produtores da lista de consumidores, dados faltantes, versões, ambiente, validade e coleta, campos distintos, conflitos, origens duplicadas, caminhos múltiplos, ciclos e limites. Também verifica que identidade e relação estrutural não viram autorização ou runtime, e que relatórios correspondem à análise.

O registro lista **testes que executamos**, não resultados de entrevistas ou ganhos de mercado. Os tempos observados localmente não são benchmark empresarial.

## O que mudou em relação ao M0

O alvo de 240 ativos está implementado no gerador. O inventário contém 512 relações coerentes, abaixo da referência inicial ajustável de 600–900; não inflamos o número com relações aleatórias. Os artefatos completos são regenerados em `build/`, não inseridos na demo pública.

Foram implementados contrato lógico, gerador, validador, oráculo, referência de análise e exportação Markdown/JSON para os três cenários. O analisador segue escopos fechados; não é uma solução universal de impacto de mudanças. As regras estão em [13_DATA_CONTRACT.md](./13_DATA_CONTRACT.md).

## Ainda pendente

M2–M4: interface nova, filtros interativos, navegação, mapa contextual e validação de UX. M5: coletores reais, avaliação experimental e segurança operacional. Discovery com clientes também não foi executado nesta etapa.

Esta revisão **não altera** o HTML/CSS/JS público, a variante Claro, os trabalhos acadêmicos, a equipe ou arquivos pessoais. O próximo passo é a jornada CHG-001 sobre esta base, sem substituir o site antes de revisão.
