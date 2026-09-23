const nodes=[...document.querySelectorAll('.node')];
const nodeMap=Object.fromEntries(nodes.map(n=>[n.dataset.id,n]));
const stage=document.getElementById('stage');
const svg=document.getElementById('edges');
const labelLayer=document.getElementById('edgeLabels');
const modeOrder=['agent','can','did','breaks','hidden'];
let currentMode='agent',runTimers=[];

const edgeDefs=[
['sales-agent','sales-role','auth','HAS_IDENTITY'],
['sales-role','customer-mcp','auth','ALLOWED_TO_USE'],
['customer-mcp','customer-api','runtime','CALLS'],
['customer-api','customer-service','runtime','ROUTES_TO'],
['customer-service','customers-table','runtime','READS_FROM'],
['customers-table','cpf','runtime','CONTAINS'],
['customer-api','crm-app','runtime','SERVES'],
['analytics-agent','customer-api','dormant','CONFIGURED_FOR'],
['legacy-service','customers-table','conflict','READS_FROM']
];

function center(el){const a=el.getBoundingClientRect(),s=stage.getBoundingClientRect();return{x:(a.left+a.width/2-s.left)/s.width*1200,y:(a.top+a.height/2-s.top)/s.height*620}}
function defs(){return '<defs><marker id="arrow-auth" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#59ddfa"/></marker><marker id="arrow-runtime" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#68eaa9"/></marker><marker id="arrow-dormant" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#75694a"/></marker><marker id="arrow-conflict" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#ff7079"/></marker></defs>'}
function draw(){
svg.innerHTML=defs();labelLayer.innerHTML='';
edgeDefs.forEach(([a,b,t,label])=>{const p1=center(nodeMap[a]),p2=center(nodeMap[b]),dx=Math.max(42,Math.abs(p2.x-p1.x)*.42),p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',`M ${p1.x} ${p1.y} C ${p1.x+dx} ${p1.y}, ${p2.x-dx} ${p2.y}, ${p2.x} ${p2.y}`);p.setAttribute('class',`edge ${t}`);p.setAttribute('marker-end',`url(#arrow-${t})`);p.dataset.from=a;p.dataset.to=b;p.dataset.type=t;p.dataset.label=label;svg.appendChild(p);const l=document.createElement('div');l.className='edge-label';l.textContent=label;l.dataset.from=a;l.dataset.to=b;l.style.left=((p1.x+p2.x)/2/1200*100)+'%';l.style.top=((p1.y+p2.y)/2/620*100)+'%';labelLayer.appendChild(l)});
}

const D={
agent:{title:'Quando um agente entra em produção, sabemos realmente o que ele consegue alcançar?',subtitle:'Agentes modernos têm identidade, tools, MCPs, APIs, modelos e acesso a dados. O desafio é correlacionar essas relações com evidência.',scenario:'AGENT RISK REVIEW',caption:'Sales Agent · identity → tools → APIs → data',detail:'Sales Agent',kicker:'AGENT PROFILE',badge:'MEDIUM RISK',copy:'Agente de produção com identidade própria, tools via MCP e acesso autorizado a dados de clientes.',metrics:[['APIs allowed','7'],['APIs observed','3'],['Sensitive data','2'],['External dest.','1']],score:'5 / 5 sinais',evidence:[['Declarado','3 tools configuradas','yes','SIM'],['Estático','clients e rotas resolvidos','yes','SIM'],['Autorização','7 APIs via scopes','yes','SIM'],['Runtime','3 APIs observadas','yes','SIM'],['Lineage','2 datasets sensíveis','yes','SIM']],insight:'Um agente moderno não é só um modelo: é uma identidade com ferramentas, permissões e caminhos de dados.',answer:['AGENT REVIEW','O que este agente consegue alcançar?','7 APIs autorizadas, 3 observadas, 2 datasets sensíveis e 1 destino externo.'],callout:['Agent-first','O agente é o ponto de entrada; o Evidence Graph reconstrói o que ele pode e realmente consegue alcançar.'],stage:['AGENTIC AI READINESS','O agente tem 7 APIs autorizadas, 3 observadas e alcança 2 datasets sensíveis.'],notes:['Comece pelo agente','Um agente moderno não é apenas um LLM: ele possui identidade, tools, MCPs, APIs e acesso a dados.'],hot:['sales-agent','sales-role','customer-mcp','customer-api','customer-service','customers-table','cpf'],pairs:[['sales-agent','sales-role'],['sales-role','customer-mcp'],['customer-mcp','customer-api'],['customer-api','customer-service'],['customer-service','customers-table'],['customers-table','cpf']],labels:'active',stack:true},
can:{title:'CAN IT? · o caminho existe e está autorizado?',subtitle:'Reachability não é apenas topologia: identidade, escopo e política precisam fazer parte da resposta.',scenario:'AUTHORIZED REACHABILITY',caption:'Sales Agent → customers.cpf',detail:'Sales Agent → customers.cpf',kicker:'RESULTADO DE REACHABILITY',badge:'AUTHORIZED',copy:'Existe um caminho técnico e autorizado entre a identidade do agente e a coluna sensível.',metrics:[['Can reach','YES'],['Path hops','6'],['Blocked','0'],['Confidence','HIGH']],score:'4 / 5 sinais',evidence:[['Declarado','Agent usa get_customer','yes','SIM'],['Estático','tool mapeia rota /customers','yes','SIM'],['Autorização','scope customer.read','yes','SIM'],['Runtime','não é necessário p/ CAN IT','unknown','N/A'],['Lineage','Service → table → cpf','yes','SIM']],insight:'Um caminho técnico sem permissão não deveria resultar em CAN IT = YES. A autorização faz parte do traversal.',answer:['CAN IT?','O Sales Agent consegue alcançar CPF?','Sim. Há um caminho completo e autorizado até customers.cpf.'],callout:['Reachability','A análise atravessa identidade → permissão → MCP → API → serviço → dado.'],stage:['AUTHORIZED PATH','O caminho só é válido porque topologia e permissão concordam.'],notes:['Explique reachability','Mostre que não basta existir uma conexão técnica. A identidade precisa ter permissão para atravessar o caminho.'],hot:['sales-agent','sales-role','customer-mcp','customer-api','customer-service','customers-table','cpf'],pairs:[['sales-agent','sales-role'],['sales-role','customer-mcp'],['customer-mcp','customer-api'],['customer-api','customer-service'],['customer-service','customers-table'],['customers-table','cpf']],labels:'active',stack:false},
did:{title:'DID IT? · possibilidade e comportamento real são fatos diferentes.',subtitle:'Runtime telemetry reduz o espaço entre a arquitetura imaginada e a arquitetura realmente executada.',scenario:'RUNTIME EVIDENCE',caption:'Caminho observado em produção',detail:'Observed path · Sales Agent',kicker:'RUNTIME RESULT',badge:'OBSERVED',copy:'O caminho foi efetivamente visto na telemetria; dependências apenas configuradas ficam visualmente separadas.',metrics:[['Observed','YES'],['Calls / 30d','183'],['Last seen','3m'],['DB reads','179']],score:'5 / 5 sinais',evidence:[['Declarado','get_customer configurado','yes','SIM'],['Estático','API → Customer Service','yes','SIM'],['Autorização','customer.read válido','yes','SIM'],['Runtime','183 chamadas + 179 reads','yes','SIM'],['Lineage','table contém cpf','yes','SIM']],insight:'Se algo pode acontecer mas nunca foi observado, isso não prova que não exista — mas muda o grau de confiança de que seja uma dependência ativa.',answer:['DID IT?','O agente realmente percorreu esse caminho?','Sim. Há traces do agente até a API e spans de leitura no banco.'],callout:['Runtime evidence','O grafo diferencia CAN_CALL de CALLS_OBSERVED em vez de colapsar as duas coisas.'],stage:['OBSERVED IN PRODUCTION','As linhas verdes animadas representam dependências efetivamente vistas em runtime.'],notes:['Destaque “possível ≠ observado”','A permissão mostra o que pode acontecer. O runtime mostra o que realmente aconteceu. São fatos diferentes.'],hot:['sales-agent','customer-mcp','customer-api','customer-service','customers-table','cpf'],pairs:[['customer-mcp','customer-api'],['customer-api','customer-service'],['customer-service','customers-table'],['customers-table','cpf']],labels:'active',stack:false},
breaks:{title:'WHAT BREAKS? · blast radius potencial não é igual a blast radius ativo.',subtitle:'Uma mudança pode afetar consumidores configurados, mas os traces ajudam a priorizar o que realmente está em uso.',scenario:'CHANGE IMPACT',caption:'Simulação: cpf muda de string → integer',detail:'GET /customers/{id}',kicker:'CHANGE IMPACT',badge:'CHANGE',copy:'O contrato mudou. O protótipo separa consumidores ativos, observados e apenas configurados.',metrics:[['Potential','3'],['Observed','2'],['Dormant','1'],['Critical','2']],score:'4 / 5 sinais',evidence:[['Declarado','3 consumidores conhecidos','yes','SIM'],['Estático','Analytics Agent referencia API','yes','SIM'],['Autorização','Sales Agent autorizado','yes','SIM'],['Runtime','2 consumidores ativos','yes','SIM'],['Lineage','API alcança customers.cpf','yes','SIM']],insight:'O objetivo não é ignorar dependências dormentes, e sim mostrar prioridade e incerteza em vez de entregar uma lista plana.',answer:['WHAT BREAKS?','Quem é afetado se o contrato mudar?','CRM Web e Sales Agent estão ativos; Analytics Agent aparece como risco potencial, mas dormente.'],callout:['Active blast radius','Potential = 3, observed = 2. A diferença reduz ruído e melhora priorização.'],stage:['SIMULATED CHANGE','cpf: string → integer · 2 consumidores ativos · 1 dependência dormente'],notes:['Mostre a priorização','O lineage poderia listar três consumidores. O runtime ajuda a separar dois ativos de um consumidor dormente.'],hot:['customer-api','customer-mcp','sales-agent','crm-app','analytics-agent'],pairs:[['customer-mcp','customer-api'],['customer-api','crm-app'],['analytics-agent','customer-api']],labels:'active',stack:false},
hidden:{title:'Conflito · o runtime pode revelar uma arquitetura que ninguém documentou.',subtitle:'A discordância entre fontes não é erro para esconder; ela própria pode ser um sinal operacional.',scenario:'EVIDENCE CONFLICT',caption:'Legacy Exporter apareceu em runtime, mas não existe no catálogo',detail:'Legacy Exporter → customers',kicker:'DEPENDÊNCIA OCULTA',badge:'CONFLICT',copy:'Uma leitura do banco foi observada, apesar de a dependência não existir na arquitetura declarada.',metrics:[['Declared','NO'],['Observed','YES'],['Last seen','12m'],['Severity','HIGH']],score:'1 conflito',evidence:[['Declarado','nenhuma relação encontrada','no','NÃO'],['Estático','serviço não mapeado','no','NÃO'],['Autorização','identidade não resolvida','unknown','UNKNOWN'],['Runtime','read observado há 12m','warn','SIM'],['Lineage','customers é fonte do serviço','warn','INFERIDO']],insight:'O sistema não deveria “resolver” o conflito silenciosamente. Ele deve expor que runtime, documentação e identidade contam histórias diferentes.',answer:['CONFLICT','Existe algo que o catálogo não conhece?','Sim. Legacy Exporter acessou customers em produção sem dependência declarada.'],callout:['Hidden dependency','Runtime = YES, declared = NO. Esse desacordo vira uma descoberta investigável.'],stage:['ARCHITECTURE DRIFT','Runtime observou uma dependência que não aparece no catálogo nem na análise estática.'],notes:['Feche com o conflito','Essa é a parte mais “pesquisa”: fontes discordam. Em vez de apagar a divergência, o Evidence Graph a transforma em sinal.'],hot:['legacy-service','customers-table'],pairs:[['legacy-service','customers-table']],labels:'active',stack:false}
};

function renderEvidence(items){document.getElementById('evidenceMatrix').innerHTML=items.map(([type,detail,kind,label])=>`<div class="evidence-row"><span class="ev-type">${type}</span><span class="ev-detail">${detail}</span><span class="signal ${kind}">${label}</span></div>`).join('')}
function setMetrics(items){document.getElementById('metrics').innerHTML=items.map(([a,b])=>`<div><span>${a}</span><b>${b}</b></div>`).join('')}
function setAnswer(a){document.getElementById('answerBox').innerHTML=`<span class="answer-label">${a[0]}</span><strong>${a[1]}</strong><p>${a[2]}</p>`}
function setCallout(a){document.getElementById('storyCallout').innerHTML=`<span class="callout-icon">◇</span><div><b>${a[0]}</b><span>${a[1]}</span></div>`}
function setStage(a){document.getElementById('stageNote').innerHTML=`<span>${a[0]}</span><b>${a[1]}</b>`}
function setNotes(a){document.getElementById('notesTitle').textContent=a[0];document.getElementById('notesText').textContent=a[1]}

function clearRun(){
runTimers.forEach(clearTimeout);runTimers=[];
nodes.forEach(n=>n.classList.remove('run-active','auth-run','runtime-run'));
[...svg.querySelectorAll('.edge')].forEach(e=>e.classList.remove('run-active','auth-run','runtime-run'));
document.querySelectorAll('[data-trace]').forEach(x=>x.classList.remove('active','auth-active','runtime-active'));
document.getElementById('traceStatus').textContent='ready';
}
function simulateRun(){
clearRun();
setMode('did');
document.getElementById('traceStatus').textContent='authorization check';
document.getElementById('stageNote').innerHTML='<span>AUTHORIZATION CHECK</span><b>Validando identidade sales-prod-role e scope customer.read antes da execução.</b>';

const authSeq=['sales-agent','sales-role','customer-mcp'];
authSeq.forEach((id,i)=>{
  runTimers.push(setTimeout(()=>{
    nodeMap[id]?.classList.add('auth-run');
    document.querySelector(`[data-trace="${id}"]`)?.classList.add('auth-active');
    if(i>0){
      const prev=authSeq[i-1];
      [...svg.querySelectorAll('.edge')].find(e=>e.dataset.from===prev&&e.dataset.to===id)?.classList.add('auth-run');
    }
    if(id==='customer-mcp'){
      document.getElementById('traceStatus').textContent='authorized · runtime starting';
      document.getElementById('stageNote').innerHTML='<span>AUTHORIZED</span><b>sales-prod-role possui customer.read e pode usar get_customer. Agora começa o runtime trace.</b>';
    }
  },i*520));
});

const runtimeSeq=['customer-mcp','customer-api','customer-service','customers-table','cpf'];
runtimeSeq.forEach((id,i)=>{
  runTimers.push(setTimeout(()=>{
    nodeMap[id]?.classList.add('runtime-run');
    document.querySelector(`[data-trace="${id}"]`)?.classList.add('runtime-active');
    if(i>0){
      const prev=runtimeSeq[i-1];
      [...svg.querySelectorAll('.edge')].find(e=>e.dataset.from===prev&&e.dataset.to===id)?.classList.add('runtime-run');
    }
    if(i===0){
      document.getElementById('traceStatus').textContent='runtime trace';
      document.getElementById('stageNote').innerHTML='<span>RUNTIME TRACE</span><b>Execução observada: MCP tool → API → Service → Table → PII.</b>';
    }
    if(i===runtimeSeq.length-1){
      document.getElementById('traceStatus').textContent='complete · 428 ms';
      document.getElementById('stageNote').innerHTML='<span>TRACE COMPLETE</span><b>Authorization ✓ · Sales Agent → get_customer → API → Service → customers → CPF · policy: allowed</b>';
    }
  },(authSeq.length*520)+350+(i*520)));
});
}
function setMode(mode){
clearRun();currentMode=mode;const c=D[mode]||D.agent;
document.querySelectorAll('[data-mode]').forEach(x=>x.classList.toggle('active',x.dataset.mode===mode));
document.getElementById('title').textContent=c.title;document.getElementById('subtitle').textContent=c.subtitle;document.getElementById('scenarioLabel').textContent=c.scenario;document.getElementById('caption').textContent=c.caption;document.getElementById('detailTitle').textContent=c.detail;document.getElementById('kicker').textContent=c.kicker;document.getElementById('badge').textContent=c.badge;document.getElementById('detailCopy').textContent=c.copy;document.getElementById('insight').textContent=c.insight;document.getElementById('evidenceScore').textContent=c.score;document.getElementById('agentStack').style.display=c.stack?'grid':'none';
setMetrics(c.metrics);renderEvidence(c.evidence);setAnswer(c.answer);setCallout(c.callout);setStage(c.stage);setNotes(c.notes);document.getElementById('stepLabel').textContent=String(modeOrder.indexOf(mode)+1).padStart(2,'0')+' / 05';
nodes.forEach(n=>{n.classList.remove('dim','hot','hot-runtime','hot-break','hot-conflict');if(n.dataset.id==='legacy-service'){n.style.opacity=mode==='hidden'?'1':'0';n.style.pointerEvents=mode==='hidden'?'auto':'none'}if(mode!=='agent'&&!c.hot.includes(n.dataset.id))n.classList.add('dim');if(c.hot.includes(n.dataset.id))n.classList.add(mode==='did'?'hot-runtime':mode==='breaks'?'hot-break':mode==='hidden'?'hot-conflict':'hot')});
[...svg.querySelectorAll('.edge')].forEach(e=>{e.classList.remove('dim','hot');const active=(c.pairs||[]).some(([a,b])=>e.dataset.from===a&&e.dataset.to===b);if(mode!=='agent'&&!active)e.classList.add('dim');if(active)e.classList.add('hot')});
document.querySelectorAll('.edge-label').forEach(l=>{const active=(c.pairs||[]).some(([a,b])=>l.dataset.from===a&&l.dataset.to===b);l.style.opacity=c.labels==='all'?'.8':active?'1':'0'});
}
function step(delta){let i=modeOrder.indexOf(currentMode);i=(i+delta+modeOrder.length)%modeOrder.length;setMode(modeOrder[i])}
function toggleNotes(force){const n=document.getElementById('presenterNotes');n.classList.toggle('open',force===undefined?!n.classList.contains('open'):force)}
function togglePresentation(){document.body.classList.toggle('presentation');setTimeout(draw,220)}
async function toggleFullscreen(){if(!document.fullscreenElement)await document.documentElement.requestFullscreen?.();else await document.exitFullscreen?.()}

document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode)));
document.getElementById('prevBtn').addEventListener('click',()=>step(-1));document.getElementById('nextBtn').addEventListener('click',()=>step(1));
document.getElementById('search').addEventListener('keydown',e=>{if(e.key==='Enter')setMode('agent')});
document.getElementById('simulateRunBtn').addEventListener('click',simulateRun);
document.getElementById('fullscreenBtn').addEventListener('click',toggleFullscreen);document.getElementById('notesBtn').addEventListener('click',()=>toggleNotes());document.getElementById('closeNotes').addEventListener('click',()=>toggleNotes(false));
document.addEventListener('keydown',e=>{if(['INPUT','TEXTAREA'].includes(document.activeElement?.tagName))return;if(e.key==='ArrowRight')step(1);if(e.key==='ArrowLeft')step(-1);if(/^[1-5]$/.test(e.key))setMode(modeOrder[Number(e.key)-1]);if(e.key.toLowerCase()==='p')togglePresentation();if(e.key.toLowerCase()==='n')toggleNotes();if(e.key.toLowerCase()==='f')toggleFullscreen();if(e.key==='Escape')toggleNotes(false)});
nodes.forEach(n=>n.addEventListener('click',()=>{if(n.dataset.id==='sales-agent')setMode('agent');if(n.dataset.id==='cpf')setMode('can');if(n.dataset.id==='customer-api')setMode('breaks');if(n.dataset.id==='legacy-service')setMode('hidden')}));
window.addEventListener('resize',()=>{draw();setMode(currentMode)});
draw();setMode('agent');