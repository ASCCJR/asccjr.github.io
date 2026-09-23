# Roteiro de apresentação — Evidence Graph

**Duração alvo:** 4 minutos  
**Demo:** https://asccjr.github.io/evidence-graph/

---

## 1. Abertura — tela inicial / Agent Review

> “Esse projeto começou a partir de uma ideia de lineage e governança envolvendo dados, APIs e agentes de IA.  
> No início eu pensei em um grande grafo corporativo, mas pesquisando o estado da arte percebi que partes importantes disso já existem em soluções como DataHub, Atlan, Holistic AI e Sensedia.  
> Então a pergunta mudou: hoje eu quero investigar se a fusão de diferentes tipos de evidência melhora a análise de dependências.”

Aponte para:

`CONFIG · CODE · IAM · OTEL · LINEAGE`

> “Essas são as cinco fontes que eu quero correlacionar: configuração, código, autorização, runtime e lineage.”

Depois:

> “Hoje eu classificaria o projeto como pesquisa aplicada com potencial de invenção. Ainda não como inovação, porque ele não foi aplicado em ambiente real nem gerou valor mensurável.”

---

## 2. Agent Review

Aponte para **Sales Agent** e para o painel da direita.

> “Eu começo pelos agentes porque esse problema fica muito evidente na era agentic. Um agente moderno não é apenas um LLM: ele tem identidade, permissões, tools, MCPs, APIs e acesso a dados.”

Mostre:

- APIs allowed;
- APIs observed;
- Sensitive data;
- External destination.

> “Nesse exemplo sintético, o agente possui sete APIs autorizadas, mas apenas três foram observadas em execução.”

---

## 3. Clique em **Simulate agent run**

### Primeiro: Authorization Check

Espere o destaque passar por:

`Sales Agent → sales-prod-role → get_customer`

> “Antes da execução, eu separo uma etapa de autorização. Aqui o sistema verifica a identidade do agente, o scope customer.read e se ele pode usar a tool.”

Quando aparecer **AUTHORIZED**:

> “Isso responde se o caminho é permitido. Ainda não significa que ele realmente aconteceu.”

### Depois: Runtime Trace

Espere a animação seguir:

`get_customer → API → Service → customers → CPF`

> “Agora começa o runtime. Essa parte representaria evidências reais vindas, por exemplo, de OpenTelemetry, gateway traces e logs do banco.”

Quando chegar em **CPF**:

> “Então conseguimos separar claramente: autorizado é uma coisa; observado em execução é outra.”

---

## 4. Clique em **CAN IT?**

> “A primeira pergunta central é CAN IT?: esse agente consegue alcançar determinado recurso?”

Aponte para o caminho completo.

> “A resposta combina topologia com identidade e permissão. Não basta existir uma conexão técnica; o caminho também precisa estar autorizado.”

---

## 5. Clique em **DID IT?**

> “A segunda pergunta é DID IT?: esse acesso realmente aconteceu?”

Mostre:

- Calls / 30d;
- Last seen;
- DB reads.

> “Aqui entram as evidências de runtime. Isso permite distinguir arquitetura possível de arquitetura realmente ativa.”

---

## 6. Clique em **WHAT BREAKS?**

> “A terceira pergunta é WHAT BREAKS?: se uma API, um schema ou uma tool mudar, quais consumidores podem ser afetados?”

Aponte para:

- Potential;
- Observed;
- Dormant;
- Critical.

> “A proposta é não entregar apenas uma lista plana de dependências. O sistema separa o que é potencial, o que foi observado e o que está dormente, para tornar o blast radius mais útil.”

---

## 7. Clique em **Conflito**

Mostre a matriz:

`Declarado: NÃO · Estático: NÃO · Runtime: SIM`

> “Essa é a parte que considero mais interessante para pesquisa: as fontes podem discordar. Aqui o runtime encontrou uma dependência que não existe no catálogo nem na análise estática.”

> “Em vez de apagar essa divergência, o Evidence Graph transforma o conflito em uma descoberta investigável.”

---

## 8. Fechamento — invenção x inovação

> “Lineage, knowledge graph, OpenTelemetry e governança de agentes não são novidades deste projeto. A hipótese de contribuição é mais específica: verificar se a fusão dessas evidências permite classificar melhor dependências como possíveis, autorizadas, observadas ou conflitantes.”

> “Se essa contribuição se provar tecnicamente diferenciada, ela pode gerar protótipo, artigo ou eventualmente algo patenteável. Se depois for aplicada numa empresa e gerar valor real, aí passamos da invenção para a inovação.”

> “O próximo passo seria substituir as evidências simuladas por collectors reais e medir precision, recall, falsos positivos e falsos negativos.”

Finalize:

> “Minha principal dúvida é qual seria o menor escopo experimental que ainda permitiria demonstrar uma contribuição real.”

---

## Sequência de cliques

```text
1. Agent Review
2. Simulate agent run
   2.1 Authorization Check
   2.2 Runtime Trace
3. CAN IT?
4. DID IT?
5. WHAT BREAKS?
6. Conflito
7. Fechamento
```
