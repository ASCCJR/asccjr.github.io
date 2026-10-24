# EvidentGraph Core — próximas etapas após L2

**Data:** 2026-10-16  
**Estado:** roteiro de desenvolvimento; somente a estabilização L3 abaixo foi iniciada.  
**Escopo:** Core; manter GitHub Pages, grafo + lista e identidade Grupo Aurora. Não altera Campus Mobile.

**Leitura histórica, reconciliada em 20/10/2026:** o estado e a sequência abaixo foram escritos após L2. L3–L7 avançaram nos limites dos checkpoints posteriores; não reiniciar essas etapas a partir deste roteiro. O estado atual está em [00_START_HERE.md](./00_START_HERE.md) e [30_L7_EVIDENCE_REVIEW.md](./30_L7_EVIDENCE_REVIEW.md). A próxima frente estratégica é a [proposta CTE-IA](../../opportunities/cte-ia-2026/README.md), sem L8, novo parser ou deploy como pré-requisito. Pesquisa, produto e edital continuam neste mesmo ambiente, preservando a separação entre o Core e cada oportunidade.

## Onde estamos

A M3 apresenta o inventário sintético maior. O laboratório L1 executa HTTP/SQLite e captura spans; a ponte L2 permite visualizar a captura na mesma experiência, em um conjunto separado. A análise continua delimitada a contratos e clientes de teste conhecidos.

Ainda não há coleta empresarial contínua, IAM efetivo, agente com modelo de linguagem no laboratório, piloto com cliente, ganho de precisão demonstrado ou produto de produção. Um teste passar não elimina essas lacunas.

## Sequência de trabalho

| Etapa | Entrega proposta | Critério para avançar |
|---|---|---|
| **L3 — estabilizar uso e reprodução** | Troca de fonte, recarga, notas, exportação e testes de navegador por HTTP. Manter a interface existente. | Resultado reproduzível sem perder/misturar notas; falha de armazenamento explicitada; CI executado e revisado. |
| **L4 — novas capturas sem remontagem manual** | Um comando local para executar, validar, versionar e preparar uma captura. Histórico por ID/hash e comparação entre capturas compatíveis. | Uma nova execução muda as evidências e a visualização; a anterior permanece rastreável. Nenhuma captura histórica é rotulada como ao vivo. |
| **L5 — um caminho autorizado e uma ferramenta** | Identidade de teste, política local explícita, uma ferramenta/API e casos permitido, negado e indeterminado. Incluir um cliente não agente. | Política configurada, decisão aplicada e chamada observada são respostas separadas. Tentativa negada não conta como acesso bem-sucedido. |
| **L6 — experimento de fusão de evidências** | Casos com oráculos independentes; comparação das fontes isoladas e combinadas. | Medir erro, cobertura e desconhecimento sem usar a própria regra como verdade de referência. Registrar também ausência de ganho. |
| **Piloto e edital do Core** | Uma equipe, um fluxo, integração de leitura limitada, entregáveis e critérios combinados. Proposta-base de P&D. | Evidência de utilidade e compromisso real do participante; orçamento e prazo baseados no trabalho delimitado. |

Etapas são prioridades, não datas prometidas. Não implementar os cinco blocos de uma vez. A passagem para publicação depende de revisão explícita; este roteiro não autoriza automaticamente merge, deploy ou acesso a dados de terceiros.

## L3 — estabilização em curso

A fonte passa a usar `?source=lab` ou `?source=aurora`; links antigos `#aurora` são reconhecidos. Isso evita compartilhar o mesmo fragmento com o link de acessibilidade `#main`. A troca carrega um conjunto inteiro, sem unir origens.

Quando o armazenamento falha, a interface avisa que as notas são temporárias e permite cancelar a troca de fonte para exportá-las primeiro. O aviso não promete recuperação de dados já perdidos nem sincronização entre dispositivos.

Uma suíte de 12 casos exercita navegação HTTP real em Chromium: recursos, troca, recarga, notas por fonte/captura, links antigos, âncora de acessibilidade, voltar/avançar, falha de armazenamento, exportação e HTML único. Seu resultado depende de execução, não da existência do arquivo de teste.

Registro: [25_L3_BROWSER_VALIDATION.md](./25_L3_BROWSER_VALIDATION.md).

## L4 — reduzir o trabalho manual

Primeiro automatizar execução e preparação em lote. Não chamar esse processo de streaming ou monitoramento contínuo.

Cada captura deve preservar intervalo, origem, versões, checksum, resultado e limitações. Reexecução não sobrescreve a anterior. A comparação só pode concluir mudança quando entidade, ambiente e escopo são compatíveis; menos traces podem significar menos cobertura, não remoção de dependência.

A leitura inicial continua local e limitada ao esquema conhecido. Uma interface de importação universal não faz parte dessa etapa. Conectores de produção, refresh automático e gestão de credenciais exigem especificação própria.

## L5 — tornar CAN IT? verificável

Adicionar autorização de laboratório antes de prometer governança real. Avaliar uma combinação explícita de identidade, ação e recurso; não concluir permissão de coluna a partir de um scope genérico.

Usar ao menos três casos: acesso permitido e executado, negado e não concluído, e configuração insuficiente para avaliar. Registrar negativa como tentativa, não como leitura. Não expor chaves ou dados de produção.

Uma ferramenta MCP é candidata para essa etapa. Um consumidor roteirizado é útil para testes determinísticos, mas não deve ser anunciado como agente autônomo. Um agente com modelo poderá entrar depois, com provedor, custo, credenciais e critérios de comportamento definidos. Agentes permanecem um caso de uso, não o limite do Core.

## L6 — testar a contribuição, não apenas o código

O laboratório atual usa requisitos declarados compartilhados pelo cliente de teste e pelo comparador. Portanto, não é ainda prova independente de contribuição científica.

Separar três alvos: dependência possível, uso observado e incompatibilidade de uma mudança específica. Preparar respostas de referência independentes, casos não usados na construção e mutações: fonte ausente, desatualizada, conflito, chamada negada, execução esporádica e caminhos duplicados.

Comparar as mesmas perguntas sob configuração/contrato, runtime e combinação; adicionar autorização apenas quando implementada. Relatar precisão/recall quando houver referência apropriada, falsos positivos/negativos, cobertura, respostas indeterminadas e tempo de investigação. Falta de trace não vira negativo para aumentar a acurácia.

## Discovery e UX — em paralelo, desde agora

Começar com 3–5 sessões exploratórias, não uma amostra estatística. Usar [22_ROTEIRO_AVALIACAO_M3.md](./22_ROTEIRO_AVALIACAO_M3.md), pedindo que a pessoa encontre consumidores, responsáveis e lacunas sem explicação de cada clique.

Depois investigar o processo atual: caso recente, frequência, ferramentas, tempo gasto e consequência. Consultar quem usa, quem autoriza integração e quem poderia contratar. Interesse de colegas e professor não equivale a compra nem a validação com empresa.

Consolidar problemas observados e uma revisão de cada vez. Não iniciar outro redesenho ou aumentar nós apenas para impressionar. Nenhuma entrevista é registrada como feita até ocorrer.

## Piloto e proposta-base para edital

Buscar um fluxo real restrito, com autorização da organização e acesso mínimo. Metadados também podem ser sensíveis. Começar fora de produção e combinar dados permitidos, responsáveis, descarte e medidas de sucesso.

O pacote de P&D deve distinguir o que existe, o que será construído, entregáveis verificáveis, método experimental, riscos e custos. Evidência técnica, usabilidade e viabilidade comercial são partes diferentes. Não inventar TRL, novidade, economia ou redução de incidentes.

Conectores para Databricks, outros catálogos e gateways só entram quando responderem a necessidade observada e houver autorização. Neo4j/PostgreSQL, múltiplas organizações, segurança operacional e infraestrutura são decisões condicionadas ao próximo recorte, não requisitos para testar esta interface.

## Limites preservados

Não reabrir Sites; não remover lineage; não substituir o conjunto grande pelo laboratório pequeno; não mudar arquivos de equipe, currículo, entregas acadêmicas ou variante da Claro. Não alterar o Pages sem etapa explícita de publicação. O PR #3 é o lugar desta continuidade; conferir seu status antes de retomar.

Fontes internas: [M3](./18_ASSET_INVESTIGATION.md), [L1](./21_RETOMADA_CORE_E_LABORATORIO.md), [L2](./23_LAB_EVIDENCE_UI.md), contrato e roadmap anteriores. O roteiro é uma proposta de execução a partir desses marcos, não uma lista de capacidades já concluídas.
