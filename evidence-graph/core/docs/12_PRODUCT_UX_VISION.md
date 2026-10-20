# EvidentGraph — Visão de produto e experiência do usuário

**Data:** 2026-10-13  
**Versão:** 0.1 — especificação da próxima experiência do Core  
**Status:** direção de produto registrada; implementação e validação pendentes  
**Escopo:** EvidentGraph Core. Não modifica a variante Campus Mobile nem substitui a demo pública nesta etapa.

**Reconciliação em 20/10/2026:** este texto preserva a proposta de 13/10 e suas metas então não implementadas. A restauração posterior do grafo e a implementação M3/L7 prevalecem: grafo/lineage, lista e análise operacional juntos; Grupo Aurora 240 ativos/512 relações, separado dos laboratórios. Consultar checkpoints 17, 18 e 30 e o índice atual, sem reconstruir telas a partir das especificações antigas.

Preferências preservadas do proponente: estética empresarial sóbria, sem brilhos/slogans excessivos nem repetição de “demo” em toda tela; origem fictícia/laboratorial clara em “Sobre o ambiente”, relatórios e onde afeta a interpretação. Textos e entregas em Markdown; PDF/HTML textual somente quando solicitado. Roteiros de apresentação curtos, com ações visíveis quando pedidas. O feedback reportado do professor e dos colegas não equivale a avaliação independente com usuários ou compradores.

> O usuário não entra no EvidentGraph para admirar um grafo. Entra para entender uma consequência e decidir o que fazer.

## 1. Decisão em uma página

O EvidentGraph deve apresentar respostas operacionais antes de apresentar sua arquitetura técnica. A primeira jornada completa será **analisar o impacto de uma mudança** em uma API, com processos de negócio, consumidores, responsáveis, evidências e lacunas visíveis.

A experiência proposta é:

**Selecionar a mudança → compreender consequências → identificar responsáveis → registrar verificações → exportar a análise.**

O grafo continua fundamental para explorar caminhos. A configuração, o código, a autorização, o lineage e o runtime continuam sendo as fontes do modelo. Porém, o usuário não precisa estudar essas cinco fontes para começar a trabalhar.

Para demonstrar a experiência, construiremos um ambiente empresarial fictício maior e coerente. A referência inicial é **240 ativos**, não uma promessa de escala comprovada. Para validar a coleta e a correlação, manteremos uma **PoC pequena com integrações reais**. São entregas diferentes.

O Core continua abrangendo dados, software e IA. Agentes serão consumidores e produtores no ecossistema, não o limite do produto. Nenhum requisito de celular ou Android é incorporado ao Core por esta revisão.

## 2. Origem da revisão e limites das evidências

### Feedback recebido

Segundo o relato do proponente, um professor avaliou que a demo tem um grafo pequeno, estética pouco compatível com um sistema empresarial e foco excessivo em explicar o mecanismo. A orientação foi priorizar experiência do usuário, perguntas respondidas e visão de negócio.

Esse é um **feedback qualitativo reportado**, não uma pesquisa com clientes nem uma validação de mercado. Não atribuímos ao professor as soluções, metas numéricas ou prioridades detalhadas propostas neste documento.

### Base já existente

O [contexto canônico](./01_CANONICAL_CONTEXT.md) registra a hipótese de fusão de evidências, o caráter sintético da demonstração e a necessidade de preservar incerteza. A [visão anterior](./04_PRODUCT_VISION.md) apresenta CAN IT?, DID IT? e WHAT BREAKS?. O [roadmap](./07_MVP_ROADMAP.md) diferencia demonstração e experimento.

### O que é novo aqui

A jornada prioritária, o desenho das telas, a empresa fictícia, os critérios de aceitação e o plano de teste abaixo são **especificações propostas para o desenvolvimento**, não capacidades já implementadas ou resultados obtidos.

Esta revisão não reavalia concorrentes nem comprova ineditismo. Afirmações competitivas devem passar por pesquisa própria antes de serem usadas em uma candidatura.

## 3. Visão de negócio

### Proposta de valor a testar

> Ajudar equipes a revisar mudanças em sistemas de dados, software e IA, identificando quem pode ser afetado, por qual dependência, quem precisa participar da revisão e quais informações ainda faltam.

### Primeiro segmento e papéis — hipóteses de discovery

| Papel | Situação a investigar | Valor pretendido |
|---|---|---|
| Usuário principal: responsável técnico por uma mudança | Precisa identificar consumidores e preparar validações antes de publicar | Menos investigação manual e menos dependências relevantes esquecidas |
| Colaborador: responsável por um sistema consumidor | Precisa saber se a mudança exige ação de sua equipe | Contexto claro, evidência acessível e tarefa de validação específica |
| Possível comprador: liderança de Engenharia ou Plataforma | Avalia custo operacional e previsibilidade das mudanças | Visibilidade do trabalho e benefício mensurável em um piloto |
| Aprovador de integração: Segurança ou responsável pelas fontes | Precisa controlar acesso e exposição de metadados | Escopo reduzido, minimização de dados e rastreabilidade |

O segmento inicial proposto é uma equipe que mantém serviços e pipelines interligados e consegue disponibilizar um ambiente de teste. Isso não equivale a afirmar que toda empresa enfrenta a mesma dor, que alguém pagará ou que pequenas empresas são necessariamente o melhor mercado.

### Alternativas com as quais comparar

Nas entrevistas, identificar o processo realmente usado: consulta ao código, catálogo, observabilidade, documentação, testes de contrato, conversa com responsáveis ou combinação dessas opções. Não presumir que ferramentas existentes deixam de responder à pergunta.

### Adoção e receita

Começar por um serviço ou equipe, com coleta de leitura e integração limitada. Hipótese comercial inicial: diagnóstico/piloto de escopo fechado, seguido de avaliação de uso recorrente. Preço, unidade de cobrança, comprador e disposição a pagar permanecem abertos.

Uma entrevista positiva é evidência de percepção. Aceitar um piloto é evidência de adoção potencial. Pagamento ou compromisso comercial explícito é evidência comercial mais forte. Nenhum desses sinais, isoladamente, comprova adequação de produto ao mercado.

## 4. Perguntas de trabalho e prioridade

| Jornada | Pergunta do usuário | Resposta útil | Prioridade |
|---|---|---|---|
| Análise de mudança | O que pode ser afetado por esta alteração? | Consequências a verificar, consumidores, responsáveis e lacunas | P0: jornada completa |
| Investigação de acesso | Quem tem caminhos de acesso a este dado e quais foram observados? | Caminhos, condições de autorização e observação | P1: depois da jornada principal |
| Desativação | O que falta verificar antes de remover este recurso? | Dependências conhecidas, uso e cobertura insuficiente | P1 |
| Investigação de incidente | Quais dependências merecem investigação? | Relações, alterações relevantes e hipóteses, sem declarar causa automaticamente | P2 |
| Explicação de entrega analítica | De quais dados, pipelines e modelos este dashboard depende? | Cadeia de dependências e responsáveis | Contexto navegável em P0; investigação própria em P2 |

CAN IT?, DID IT? e WHAT BREAKS? permanecem como perguntas do motor. Não precisam ser o menu principal da aplicação.

P0 não inclui implementar todas as jornadas. Inventário, mapa contextual e evidências existem para sustentar a análise de mudança. Não criar menus ativos que levam a telas vazias ou botões que fingem executar funcionalidades futuras.

## 5. Jornada principal: análise de mudança

### Caso sintético de referência — CHG-001

**Contexto:** uma empresa fictícia de comércio e distribuição planeja alterar a API de clientes.  
**Mudança:** remover `cliente_id` da resposta de `GET /customers/{id}`.  
**Ambiente:** produção sintética.  
**Decisão apoiada:** quais validações são necessárias antes da publicação?

A análise não deve concluir que todos os consumidores da API usam o campo removido. Ela precisa distinguir uma dependência da API de uma dependência específica do campo.

### Passo 1 — Escolher e delimitar

O usuário seleciona o ativo e a alteração preparada no cenário. A tela informa versão anterior e proposta, campo alterado, ambiente, janela de observação e versão do conjunto de dados. A comparação inicial é estruturada; não promete interpretar qualquer texto ou código arbitrário.

A ação é **Analisar impacto**. O resultado sempre repete o escopo analisado, inclusive quando nenhum consumidor é encontrado.

### Passo 2 — Receber uma resposta operacional

Exemplo de texto a ser produzido a partir das evidências do cenário:

> Esta mudança precisa de revisão. Há incompatibilidade de contrato identificada no consumidor de pedidos, um uso da API pelo agente de atendimento cujo consumo do campo não foi confirmado e uma dependência financeira sem cobertura de execução suficiente. Consulte os responsáveis e as verificações abaixo.

É um exemplo de saída, não uma mensagem fixa que aparece independentemente dos dados. Contagens e listas devem ser calculadas.

### Passo 3 — Ver consequências, não apenas nomes de ativos

| Consumidor sintético | Processo relacionado | Evidência prevista no cenário | Classificação | Próximo passo |
|---|---|---|---|---|
| Serviço de pedidos | Registrar pedido | Contrato exige `cliente_id`; uso recente da API | Incompatibilidade de contrato identificada; uso observado | Validar migração com a equipe Comercial |
| Agente de atendimento, via ferramenta MCP | Consultar cliente | Chamada à API observada; consumo do campo não resolvido | Impacto possível; evidência de campo insuficiente | Executar teste da consulta com a equipe Atendimento |
| Exportador financeiro | Conciliação | Configuração referencia a API; observação indisponível para a rotina | Dependência conhecida; impacto inconclusivo | Verificar rotina e contrato com a equipe Financeiro |
| Portal de acompanhamento | Consultar situação do pedido | Contrato do cenário não requer o campo removido | Sem incompatibilidade identificada no escopo analisado | Registrar limite da verificação; não declarar segurança universal |

As equipes são responsáveis fictícias, não pessoas reais. O uso por um processo de negócio deve ter vínculo explícito no dataset; não será inferido pelo nome do serviço.

A tabela terá busca, ordenação e filtros por processo, equipe, ambiente, tipo de relação e estado da evidência. A classificação de impacto e o estado de observação são colunas distintas.

### Passo 4 — Explorar e compreender

Ao abrir uma linha, o usuário vê um painel com resumo, responsável, caminho relevante e evidências. Pode aprofundar o grafo, mas não perde os filtros nem a mudança selecionada ao voltar.

A evidência detalhada mostra fonte fictícia, referência, versão, ambiente, momento da coleta, período de validade quando aplicável, cobertura conhecida e limitações. Registros derivados da mesma origem não são apresentados como confirmações independentes.

### Passo 5 — Encerrar a tarefa

O usuário registra verificações e exporta um relatório Markdown; JSON pode ser oferecido como complemento técnico. O relatório inclui escopo, resultado, consumidores distintos, processos envolvidos, responsáveis, ações sugeridas, evidências e lacunas.

Marcar uma verificação como concluída na interface registra uma ação do usuário, não uma prova de que o impacto desapareceu. A demo não envia mensagens, não cria chamados reais, não comenta em PRs e não publica mudanças.

## 6. Arquitetura de informação da próxima demo

### Mudanças — entrada principal

Lista de alterações sintéticas disponíveis, busca de ativo e ação para analisar. A tela inicial apresenta trabalho a realizar, não um mural de números ou uma explicação de pesquisa.

### Resultado da análise

Cabeçalho com mudança e escopo; conclusão com ressalvas; tabela de consequências; responsáveis; próximos passos; exportação. Indicadores, quando usados, devem abrir a lista correspondente e explicitar seu denominador.

### Inventário

Busca por nome, identificador, domínio, equipe, processo e tipo. Cada ativo tem página ou painel reutilizável. Um ativo que não participa da mudança atual não é automaticamente irrelevante ou livre de risco.

### Mapa contextual

Entrada por domínio, sistema ou ativo. Exibe apenas a vizinhança relevante, permite expandir e mostra quantos elementos ficaram ocultos pelos filtros. Agregações têm contagem verificável e podem ser abertas.

### Fontes e cobertura

Mostra quais fontes sintéticas contribuem para a análise, janela temporal e lacunas. Ausência de resultados deve ser distinguida de fonte indisponível. O painel não deve sugerir conexões reais com fornecedores.

A sequência de revelação é: **conclusão e limitações → consequências e ações → caminhos → evidências técnicas**. Incerteza que altera a decisão não fica escondida no último nível.

## 7. Contrato semântico das respostas

| Dimensão | Regra de produto |
|---|---|
| Impacto | Caminho no grafo indica dependência possível. Incompatibilidade requer evidência relativa à mudança. Falha efetiva requer teste ou ocorrência registrada. |
| Observação | Usar “observado no período”, “não observado no período com cobertura declarada” ou “cobertura insuficiente/desconhecida”. Evitar transformar silêncio em inexistência. |
| Autorização | Usar “permitido no escopo avaliado”, “negado no escopo avaliado” ou “indeterminado”. Um scope isolado não prova acesso efetivo a toda coluna alcançável. |
| Sensibilidade | Saber que uma tabela contém CPF não prova que uma chamada retornou CPF. Acesso ao campo exige evidência apropriada e correlacionada. |
| Conflito | Diferenças só são comparáveis quando entidade, ambiente, versão e tempo são compatíveis. Evidência antiga e atual pode representar mudança, não contradição. |
| Criticidade | Prioridade de negócio é atributo informado no cenário. Uso frequente e número de evidências não substituem criticidade. |
| Confiança | Na primeira versão, preferir justificativas e cobertura explícitas. Não exibir probabilidade como 0,97 sem método validado. |
| Causa | Dependência, proximidade no grafo e coincidência temporal não demonstram causa de incidente. |

“Dormante” não será usado automaticamente para toda dependência sem trace. Uma rotina mensal pode simplesmente não aparecer na janela consultada. Sem informações suficientes, a conclusão é inconclusiva.

A recomendação apoia revisão humana. Não representa garantia de segurança nem mecanismo de bloqueio.

## 8. Empresa sintética: maior, conectada e explicável

### Cenário de negócio

Usar o identificador neutro **Empresa Demo**, de comércio e distribuição. Seis domínios organizam o cenário: Comercial, Atendimento, Operações, Financeiro, Dados e Plataforma. Processos incluem pedido, atendimento ao cliente, expedição, conciliação, previsão de demanda e reposição.

A referência inicial de tamanho é:

| Tipo de ativo | Quantidade planejada |
|---|---:|
| Aplicações | 12 |
| Endpoints de API | 28 |
| Serviços | 24 |
| Pipelines e jobs | 24 |
| Tabelas | 52 |
| Colunas selecionadas para investigação | 48 |
| Dashboards | 12 |
| Modelos | 8 |
| Agentes | 8 |
| Servidores MCP e ferramentas, em conjunto | 8 |
| Identidades | 16 |
| **Total de ativos** | **240** |

Domínios, equipes e processos são entidades de contexto separadas dessa contagem. As 48 colunas não representam todos os campos de todas as tabelas; o inventário deve declarar essa cobertura parcial.

A referência é de 600–900 relações tipadas, ajustável conforme coerência. Não adicionar relações aleatórias apenas para alcançar volume. Esses números são metas do gerador, não resultados de implementação ou benchmark.

### Duas cadeias obrigatórias

**Cadeia operacional:** aplicação de pedidos → serviço de pedidos → API de clientes; agente de atendimento → ferramenta MCP → mesma API; exportador financeiro → mesma API. Assim a alteração tem consumidores de tipos e áreas diferentes.

**Cadeia analítica:** dados de pedidos → pipeline de vendas → tabela consolidada → execução de previsão → resultados previstos → dashboard de reposição. O modelo de previsão é uma dependência da execução; suas variáveis não dominam a tela destinada a avaliar impacto no dashboard.

O cenário deve conter fan-out, dependências compartilhadas, alternativas condicionais, uso recente, execução esporádica, fonte desatualizada, ausência de cobertura e referência não documentada. Relações incompatíveis entre homologação e produção não podem formar um caminho único.

### Reprodutibilidade

Usar semente fixa no gerador, identificadores estáveis, versão do dataset e relógio de simulação fixo. Datas e janelas devem ser relativas a esse relógio, não apresentadas como telemetria atual. Todo resultado exportado informa que os dados são sintéticos.

## 9. Modelo mínimo de dados e análise

**Ativo:** identificador, nome, tipo, domínio, equipe responsável, ambiente, versão, processos associados e criticidade declarada.

**Relação:** identificador, origem, destino, tipo, condição opcional, validade temporal e referências de evidência. Tipos diferentes preservam significados diferentes.

**Evidência:** fonte, família, objeto observado, referência, origem de derivação, coleta, intervalo, ambiente, versão, suporte/contradição, cobertura e limitação. Fonte coletada agora não implica observação recente.

**Mudança:** ativo afetado, versões anterior/proposta, operação, campo ou contrato alterado e escopo.

**Resultado:** consumidores únicos, caminhos justificadores, classificação de impacto, estado de observação, processos, equipes e ações sugeridas. Agregações são calculadas sobre o mesmo resultado filtrado.

### Regras mínimas do motor da demo

- Para relações consumidor → provedor, buscar consumidores a montante do recurso alterado. Para lineage origem → derivado, percorrer a direção de transformação. Não aplicar um traversal genérico ignorando os tipos.
- Identidade e autorização são contexto de avaliação, não chamadas de runtime. “Tabela contém coluna” é relação estrutural, não span de execução.
- Deduplicar ativos alcançados por vários caminhos, preservando os caminhos que justificam o resultado. Tratar ciclos e limites de profundidade explicitamente.
- Comparar evidências no mesmo ambiente, versão e janela. Referências de negócio sem confirmação ficam marcadas como hipóteses.
- Usar regras determinísticas verificáveis e templates de texto ligados ao resultado. Não exigir LLM para gerar a resposta da primeira versão.
- Casos preparados podem fornecer entradas e evidências, mas não trocar apenas o texto da tela. Alterar/remover uma evidência deve alterar o resultado correspondente.

JSON versionado pode sustentar a demo local. Isso não obriga a escolher agora o armazenamento definitivo da PoC. O grafo visível é uma representação do modelo, não a única fonte dos dados.

## 10. Três cenários de aceitação

### CHG-001 — Remoção de campo na API de clientes

Cobre a jornada principal. Deve distinguir incompatibilidade identificada, impacto possível, consumidor sem cobertura e consumidor sem incompatibilidade identificada no recorte. Exibir agentes e consumidores não agentes.

### CHG-002 — Mudança na saída da previsão de demanda

Remover uma coluna de resultados consumida pelo dashboard de reposição. O sistema deve mostrar cadeia analítica, equipe e decisão de reposição relacionada, sem transformar a experiência em explicação do algoritmo de previsão. Alterar o modelo não permite afirmar que toda previsão ficará errada.

### CHG-003 — Proposta de desativação de um serviço legado

Não há chamadas na janela curta, mas existe uma rotina mensal e a cobertura de execução está incompleta. A saída deve pedir verificação adicional. Não pode concluir que a remoção é segura.

P0 precisa concluir CHG-001 de ponta a ponta; CHG-002 e CHG-003 usam os mesmos componentes e testam generalidade e tratamento de incerteza, sem criar duas novas aplicações.

## 11. Direção visual e interação

A interface será uma ferramenta de trabalho em português, não uma apresentação comercial. A base inicial será clara e neutra, com tipografia de sistema legível, hierarquia discreta, espaçamento consistente e tabelas compactas sem microtexto.

Cores terão função semântica; alertas também terão rótulo e ícone. Retirar brilhos, pulsação permanente, slogans sobre IA e métricas decorativas. Animações apenas para comunicar transição ou progresso real de uma operação. A identificação “ambiente sintético” permanece visível.

Priorizar uso em notebook/desktop, sem tornar mobile obrigatório no Core. A implementação deverá ser conferida em 1366×768 e 1920×1080; zoom a 200% deve preservar acesso às informações e ações, ainda que exija rolagem.

Busca, filtros e tabela precisam funcionar pelo teclado, com foco visível. Nós do grafo devem ter acesso equivalente pelo inventário ou lista de caminhos. Tooltips não são o único lugar de informação decisiva. Modal ou painel deve abrir e fechar de forma previsível, sem perder seleção.

Três níveis do mapa: domínio/processo agregado, sistema e vizinhança da investigação. Não desenhar automaticamente os 240 ativos na primeira tela. Mostrar o que foi filtrado e permitir expandir gradualmente, inclusive quando um nó tem muitos vizinhos.

## 12. Privacidade e limites da demonstração

Usar apenas nomes de sistemas, equipes e registros inventados. Não copiar dados empresariais, currículo, contatos pessoais, credenciais ou payloads sensíveis. Para demonstrar CPF, basta classificar o campo; não é necessário armazenar documentos pessoais reais.

A demo não solicita credenciais e não envia dados a serviços externos. Evidências e exportação são locais. Uma seleção de perfil na interface, se criada para teste de UX, é simulação, não controle de acesso de produção.

Na PoC real, acesso mínimo e controle no backend são requisitos próprios. Filtros do navegador não são proteção. Não descrever coleta “somente de metadados” como ausência de risco: dependências e metadados também podem revelar informação interna.

O site atual, o histórico, os nomes da equipe e os arquivos do Campus Mobile permanecem inalterados nesta etapa documental.

## 13. Critérios de aceitação da próxima implementação

| ID | Critério verificável |
|---|---|
| UX-01 | O usuário escolhe uma mudança, vê o resultado, encontra responsáveis, registra verificações e exporta Markdown sem intervenção do apresentador. |
| UX-02 | A primeira resposta informa consequência, escopo e incerteza relevante antes dos detalhes do grafo. |
| UX-03 | Todo contador abre ou corresponde a uma lista filtrada com a mesma contagem de entidades distintas. |
| UX-04 | Busca, filtros, ordenação e retorno do painel preservam o contexto; limpar filtros restaura o conjunto esperado. |
| UX-05 | Incompatibilidade, atividade observada e criticidade são dimensões distintas; evidência insuficiente permanece visível. |
| UX-06 | CHG-001, CHG-002 e CHG-003 possuem resultados esperados documentados e verificáveis no dataset. |
| UX-07 | Dados, software, modelos e agentes aparecem em cadeias coerentes; não há ativos apenas decorativos. |
| UX-08 | Alterar uma evidência relevante modifica o resultado; textos não dependem somente do identificador da cena. |
| UX-09 | Relações, evidências e responsáveis têm identificadores válidos; não há referências órfãs ou caminhos entre ambientes indevidos. |
| UX-10 | O mapa inicia contextualizado e permite expansão; há alternativa textual aos caminhos. |
| UX-11 | Estados de nenhum resultado, cobertura parcial, fonte indisponível e entrada inválida têm mensagens e próximos passos distintos. |
| UX-12 | Teclado, foco, zoom e os dois tamanhos de tela definidos na seção 11 são verificados; nenhuma ação depende apenas de cor. |
| UX-13 | O relatório exportado corresponde ao resultado e aos filtros, registra versão/janela sintética e não promete ações externas executadas. |
| UX-14 | A implementação apresenta limitações, não finge autorização real, garantia de segurança ou capacidade de produção. |
| UX-15 | A demo anterior continua recuperável e não é substituída até revisão visual e funcional da nova experiência. |

Para desempenho, medir tempo de carregamento, filtro e expansão no navegador/equipamento de teste e publicar essas condições. Meta inicial de UX: interações comuns em até 1 segundo após carregar o dataset. É uma meta local, não um SLA ou prova de escala empresarial.

## 14. Validação: negócio, UX e pesquisa não são o mesmo teste

### Discovery de negócio — iniciar em paralelo

Proposta inicial: conversar com 5–8 profissionais que participam de mudanças, incluindo ao menos um responsável pela decisão de contratação e um responsável por integração/segurança. A amostra é exploratória, não representativa.

Pedir um caso recente: como identificaram consumidores, ferramentas usadas, pessoas envolvidas, tempo, consequência e dificuldade. Só depois mostrar o conceito. Verificar frequência da tarefa e se o processo existente já resolve bem o problema.

### Usabilidade — primeiro ciclo

Proposta: cinco sessões com tarefas usando os cenários sintéticos. Antes das sessões, registrar critérios e resultados esperados. Pedir para identificar consumidores que exigem revisão, responsável e principal lacuna, e gerar um relatório.

Medir conclusão sem ajuda, tempo, erros e interpretação de “não observado”. Meta exploratória: ao menos quatro das cinco pessoas concluírem a tarefa principal em até cinco minutos, sem interpretação de segurança garantida. Caso falhe, revisar UX; não ampliar marketing. Mesmo se passar, não chamar isso de validação de mercado.

### PoC técnica e pesquisa

Ambiente restrito: um agente, identidade/política explícita, ferramenta/API, serviço e banco, com consumidor não agente quando necessário ao teste de impacto. Primeiro usar identificadores controlados; reconciliação automática irrestrita fica fora do escopo inicial.

Preparar casos positivos, negativos e desconhecidos. Comparar configuração/metadados, acréscimo de runtime e acréscimo de autorização sobre os mesmos casos e perguntas. Separar a avaliação de dependência possível, dependência observada e incompatibilidade com a mudança: são alvos diferentes.

Medir precisão, recall, falsos positivos/negativos, cobertura, respostas inconclusivas e atualização. Não tratar desconhecido como negativo para melhorar números. Ausência de benefício também é resultado válido. O conjunto sintético maior mede coerência e UX, não precisão de coletores reais.

## 15. Sequência de implementação e pontos de controle

| Marco | Entrega | Condição para avançar |
|---|---|---|
| M0 — esta revisão | Visão, jornada, regras e critérios em Markdown | Direção registrada; sem alteração do site |
| M1 — especificar dados | Esquema, gerador, referências e respostas esperadas dos três cenários | Contagens e caminhos coerentes; nenhum dado real |
| M2 — fatia funcional | CHG-001 com lista, painel, filtros e exportação | Responde à tarefa sem depender do grafo |
| M3 — exploração | Mapa contextual e cenários CHG-002/003 | Navegação e regras de incerteza consistentes |
| M4 — avaliar UX | Testes funcionais, inspeção visual e sessões exploratórias | Registrar problemas e corrigi-los antes de publicar como substituta |
| M5 — PoC real | Coletores limitados e avaliação por condição | Evidência técnica mensurável, sem alegar escala corporativa |

Discovery e preparação da PoC podem ocorrer em paralelo. Não esperar toda a interface para conversar com usuários. Não integrar grandes catálogos apenas para dar aparência de maturidade.

Nesta revisão, M0 é a entrega. Dataset, interface nova, testes com usuários e integrações reais ainda não foram executados.

## 16. Fora de escopo e uso em editais

Ficam fora da primeira implementação: controle de acesso corporativo completo, bloqueio automático de deploy, processamento de produção, detector universal de incidentes, chatbot aberto, múltiplos conectores comerciais, faturamento, aplicativo nativo e reprodução de uma suíte de governança inteira.

A linguagem futura de candidatura deve separar:

- **Existente:** pesquisa documentada e demonstração conceitual sintética.
- **A desenvolver:** experiência operacional, dataset coerente, PoC e testes.
- **A medir:** utilidade, correção das respostas, cobertura e adoção potencial.

Não declarar redução de incidentes, economia financeira, validação de mercado, TRL ou superioridade competitiva sem evidências específicas. A demo não vira produto validado porque ficou maior ou visualmente mais sóbria.

## 17. Rastreabilidade e memória

Fontes internas consultadas: [contexto canônico](./01_CANONICAL_CONTEXT.md), [visão de produto](./04_PRODUCT_VISION.md), [roadmap](./07_MVP_ROADMAP.md), [decisões](./08_DECISION_LOG.md) e [início do Core](./00_START_HERE.md). O feedback qualitativo foi comunicado pelo proponente na conversa de 2026-10-13.

D-010 registra a mudança de demonstração centrada no mecanismo para experiência centrada em tarefas. D-011 separa demo ampliada, PoC pequena e discovery paralelo. Este documento detalha essas diretrizes; quantidades, organização das telas e metas de teste são parâmetros de projeto revisáveis, não resultados.

**Ponto de retomada:** definir o esquema e as evidências de CHG-001 antes de escrever a nova interface. Validar a resposta e a tabela de consequências primeiro; acrescentar o grafo como exploração depois.
