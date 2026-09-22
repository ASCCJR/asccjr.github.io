const nodes=[...document.querySelectorAll('.node')];
const nodeMap=Object.fromEntries(nodes.map(n=>[n.dataset.id,n]));
const stage=document.getElementById('stage');
const svg=document.getElementById('edges');

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

const modeOrder=['overview','can','did','breaks','hidden'];
let currentMode='overview';

function center(el){
  const a=el.getBoundingClientRect(),s=stage.getBoundingClientRect();
  return{x:(a.left+a.width/2-s.left)/s.width*1200,y:(a.top+a.height/2-s.top)/s.height*620};
}
function draw(){
  svg.innerHTML='';
  edgeDefs.forEach(([a,b,t,label])=>{
    const p1=center(nodeMap[a]),p2=center(nodeMap[b]);
    const dx=Math.max(42,Math.abs(p2.x-p1.x)*.42);
    const p=document.createElementNS('http://www.w3.org/2000/svg','path');
    p.setAttribute('d',`M ${p1.x} ${p1.y} C ${p1.x+dx} ${p1.y}, ${p2.x-dx} ${p2.y}, ${p2.x} ${p2.y}`);
    p.setAttribute('class',`edge ${t}`);
    p.dataset.from=a;p.dataset.to=b;p.dataset.type=t;p.dataset.label=label;
    svg.appendChild(p);
  });
  positionEdgeLabels();
}
function positionEdgeLabels(){
  document.querySelectorAll('.edge-label').forEach(label=>{
    const key=label.dataset.edgeLabel;
    const [a,b]=splitPair(key);
    const p1=center(nodeMap[a]),p2=center(nodeMap[b]);
    label.style.left=((p1.x+p2.x)/2/1200*100)+'%';
    label.style.top=((p1.y+p2.y)/2/620*100)+'%';
  });
}
function splitPair(key){
  const pairs=[
    ['sales-agent','sales-role'],['sales-role','customer-mcp'],['customer-mcp','customer-api'],
    ['customer-api','customer-service'],['customer-service','customers-table'],['customers-table','cpf']
  ];
  return pairs.find(([a,b])=>`${a}-${b}`===key)||['sales-agent','sales-role'];
}

const D={
  overview:{
    title:'Um mapa não basta. Precisamos saber por que cada relação existe.',
    subtitle:'A mesma dependência pode estar declarada, autorizada e observada — ou essas evidências podem discordar.',
    scenario:'ENTERPRISE GRAPH',
    caption:'Dados, software, identidade e agentes no mesmo modelo',
    detail:'customers.cpf',kicker:'ATIVO SELECIONADO',badge:'PII',
    copy:'Identificador pessoal alcançável por um agente através de um caminho autorizado e observado.',
    metrics:[['Can reach','YES'],['Observed','YES'],['Last seen','3m'],['Confidence','0.99']],
    score:'4 / 5 sinais',
    evidence:[
      ['Declarado','MCP tool ligado à API','yes','SIM'],
      ['Estático','Service referencia customers','yes','SIM'],
      ['Autorização','scope customer.read','yes','SIM'],
      ['Runtime','183 chamadas observadas','yes','SIM'],
      ['Lineage','customers contém cpf','yes','SIM']
    ],
    insight:'O protótipo não trata um edge como verdade absoluta. Ele preserva os sinais que sustentam cada conclusão.',
    answer:['OVERVIEW','Onde este dado entra na arquitetura?','Ele está conectado a serviço, API, MCP, identidade e agente no mesmo grafo.'],
    callout:['Ideia central','Cada edge preserva sua origem: configuração, código, autorização, lineage ou execução.'],
    hot:['cpf'],pairs:[],labelOpacity:1
  },
  can:{
    title:'CAN IT? · o caminho existe e está autorizado?',
    subtitle:'Reachability não é apenas topologia: identidade, escopo e política precisam fazer parte da resposta.',
    scenario:'AUTHORIZED REACHABILITY',
    caption:'Sales Agent → customers.cpf',
    detail:'Sales Agent → customers.cpf',kicker:'RESULTADO DE REACHABILITY',badge:'AUTHORIZED',
    copy:'Existe um caminho técnico e autorizado entre a identidade do agente e a coluna sensível.',
    metrics:[['Can reach','YES'],['Path hops','6'],['Blocked','0'],['Confidence','HIGH']],
    score:'4 / 5 sinais',
    evidence:[
      ['Declarado','Agent usa get_customer','yes','SIM'],
      ['Estático','tool mapeia rota /customers','yes','SIM'],
      ['Autorização','scope customer.read','yes','SIM'],
      ['Runtime','não é necessário p/ CAN IT','unknown','N/A'],
      ['Lineage','Service → table → cpf','yes','SIM']
    ],
    insight:'Um caminho técnico sem permissão não deveria resultar em CAN IT = YES. A autorização faz parte do traversal.',
    answer:['CAN IT?','O Sales Agent consegue alcançar CPF?','Sim. Há um caminho completo e autorizado até customers.cpf.'],
    callout:['Reachability','A análise atravessa identidade → permissão → MCP → API → serviço → dado.'],
    hot:['sales-agent','sales-role','customer-mcp','customer-api','customer-service','customers-table','cpf'],
    pairs:[['sales-agent','sales-role'],['sales-role','customer-mcp'],['customer-mcp','customer-api'],['customer-api','customer-service'],['customer-service','customers-table'],['customers-table','cpf']],
    labelOpacity:1
  },
  did:{
    title:'DID IT? · possibilidade e comportamento real são fatos diferentes.',
    subtitle:'Runtime telemetry reduz o espaço entre a arquitetura imaginada e a arquitetura realmente executada.',
    scenario:'RUNTIME EVIDENCE',
    caption:'Caminho observado em produção',
    detail:'Observed path · Sales Agent',kicker:'RUNTIME RESULT',badge:'OBSERVED',
    copy:'O caminho foi efetivamente visto na telemetria; dependências apenas configuradas ficam visualmente separadas.',
    metrics:[['Observed','YES'],['Calls / 30d','183'],['Last seen','3m'],['DB reads','179']],
    score:'5 / 5 sinais',
    evidence:[
      ['Declarado','get_customer configurado','yes','SIM'],
      ['Estático','API → Customer Service','yes','SIM'],
      ['Autorização','customer.read válido','yes','SIM'],
      ['Runtime','183 chamadas + 179 reads','yes','SIM'],
      ['Lineage','table contém cpf','yes','SIM']
    ],
    insight:'Se algo pode acontecer mas nunca foi observado, isso não prova que não exista — mas muda o grau de confiança de que seja uma dependência ativa.',
    answer:['DID IT?','O agente realmente percorreu esse caminho?','Sim. Há traces do agente até a API e spans de leitura no banco.'],
    callout:['Runtime evidence','O grafo diferencia CAN_CALL de CALLS_OBSERVED em vez de colapsar as duas coisas.'],
    hot:['sales-agent','customer-mcp','customer-api','customer-service','customers-table','cpf'],
    pairs:[['customer-mcp','customer-api'],['customer-api','customer-service'],['customer-service','customers-table'],['customers-table','cpf']],
    labelOpacity:.55
  },
  breaks:{
    title:'WHAT BREAKS? · blast radius potencial não é igual a blast radius ativo.',
    subtitle:'Uma mudança pode afetar consumidores configurados, mas os traces ajudam a priorizar o que realmente está em uso.',
    scenario:'CHANGE IMPACT',
    caption:'Simulação: cpf muda de string → integer',
    detail:'GET /customers/{id}',kicker:'CHANGE IMPACT',badge:'CHANGE',
    copy:'O contrato mudou. O protótipo separa consumidores ativos, observados e apenas configurados.',
    metrics:[['Potential','3'],['Observed','2'],['Dormant','1'],['Critical','2']],
    score:'4 / 5 sinais',
    evidence:[
      ['Declarado','3 consumidores conhecidos','yes','SIM'],
      ['Estático','Analytics Agent referencia API','yes','SIM'],
      ['Autorização','Sales Agent autorizado','yes','SIM'],
      ['Runtime','2 consumidores ativos','yes','SIM'],
      ['Lineage','API alcança customers.cpf','yes','SIM']
    ],
    insight:'O objetivo não é ignorar dependências dormentes, e sim mostrar prioridade e incerteza em vez de entregar uma lista plana.',
    answer:['WHAT BREAKS?','Quem é afetado se o contrato mudar?','CRM Web e Sales Agent estão ativos; Analytics Agent aparece como risco potencial, mas dormente.'],
    callout:['Active blast radius','Potential = 3, observed = 2. A diferença reduz ruído e melhora priorização.'],
    hot:['customer-api','customer-mcp','sales-agent','crm-app','analytics-agent'],
    pairs:[['customer-mcp','customer-api'],['customer-api','crm-app'],['analytics-agent','customer-api']],
    labelOpacity:.35
  },
  hidden:{
    title:'Conflito · o runtime pode revelar uma arquitetura que ninguém documentou.',
    subtitle:'A discordância entre fontes não é erro para esconder; ela própria pode ser um sinal operacional.',
    scenario:'EVIDENCE CONFLICT',
    caption:'Legacy Exporter apareceu em runtime, mas não existe no catálogo',
    detail:'Legacy Exporter → customers',kicker:'DEPENDÊNCIA OCULTA',badge:'CONFLICT',
    copy:'Uma leitura do banco foi observada, apesar de a dependência não existir na arquitetura declarada.',
    metrics:[['Declared','NO'],['Observed','YES'],['Last seen','12m'],['Severity','HIGH']],
    score:'1 conflito',
    evidence:[
      ['Declarado','nenhuma relação encontrada','no','NÃO'],
      ['Estático','serviço não mapeado','no','NÃO'],
      ['Autorização','identidade não resolvida','unknown','UNKNOWN'],
      ['Runtime','read observado há 12m','warn','SIM'],
      ['Lineage','customers é fonte do serviço','warn','INFERIDO']
    ],
    insight:'O sistema não deveria “resolver” o conflito silenciosamente. Ele deve expor que runtime, documentação e identidade contam histórias diferentes.',
    answer:['CONFLICT','Existe algo que o catálogo não conhece?','Sim. Legacy Exporter acessou customers em produção sem dependência declarada.'],
    callout:['Hidden dependency','Runtime = YES, declared = NO. Esse desacordo vira uma descoberta investigável.'],
    hot:['legacy-service','customers-table'],
    pairs:[['legacy-service','customers-table']],
    labelOpacity:0
  }
};

function renderEvidence(items){
  document.getElementById('evidenceMatrix').innerHTML=items.map(([type,detail,kind,label])=>`
    <div class="evidence-row">
      <span class="ev-type">${type}</span>
      <span class="ev-detail">${detail}</span>
      <span class="signal ${kind}">${label}</span>
    </div>`).join('');
}
function setMetrics(items){
  document.getElementById('metrics').innerHTML=items.map(([a,b])=>`<div><span>${a}</span><b>${b}</b></div>`).join('');
}
function setAnswer(a){
  document.getElementById('answerBox').innerHTML=`<span class="answer-label">${a[0]}</span><strong>${a[1]}</strong><p>${a[2]}</p>`;
}
function setCallout(a){
  document.getElementById('storyCallout').innerHTML=`<span class="callout-icon">◇</span><div><b>${a[0]}</b><span>${a[1]}</span></div>`;
}

function setMode(mode){
  currentMode=mode;
  const c=D[mode]||D.overview;
  document.querySelectorAll('[data-mode]').forEach(x=>x.classList.toggle('active',x.dataset.mode===mode));
  document.getElementById('title').textContent=c.title;
  document.getElementById('subtitle').textContent=c.subtitle;
  document.getElementById('scenarioLabel').textContent=c.scenario;
  document.getElementById('caption').textContent=c.caption;
  document.getElementById('detailTitle').textContent=c.detail;
  document.getElementById('kicker').textContent=c.kicker;
  document.getElementById('badge').textContent=c.badge;
  document.getElementById('detailCopy').textContent=c.copy;
  document.getElementById('insight').textContent=c.insight;
  document.getElementById('evidenceScore').textContent=c.score;
  setMetrics(c.metrics);renderEvidence(c.evidence);setAnswer(c.answer);setCallout(c.callout);

  document.getElementById('stepLabel').textContent=String(modeOrder.indexOf(mode)+1).padStart(2,'0')+' / 05';

  nodes.forEach(n=>{
    n.classList.remove('dim','hot','hot-runtime','hot-break','hot-conflict');
    if(n.dataset.id==='legacy-service'){
      n.style.opacity=mode==='hidden'?'1':'0';
      n.style.pointerEvents=mode==='hidden'?'auto':'none';
    }
    if(mode!=='overview'&&!c.hot.includes(n.dataset.id))n.classList.add('dim');
    if(c.hot.includes(n.dataset.id)){
      n.classList.add(mode==='did'?'hot-runtime':mode==='breaks'?'hot-break':mode==='hidden'?'hot-conflict':'hot');
    }
  });

  [...svg.querySelectorAll('.edge')].forEach(e=>{
    e.classList.remove('dim','hot');
    const active=(c.pairs||[]).some(([a,b])=>e.dataset.from===a&&e.dataset.to===b);
    if(mode!=='overview'&&!active)e.classList.add('dim');
    if(active)e.classList.add('hot');
  });

  document.querySelectorAll('.edge-label').forEach(l=>l.style.opacity=String(c.labelOpacity));
}

function step(delta){
  let i=modeOrder.indexOf(currentMode);
  i=(i+delta+modeOrder.length)%modeOrder.length;
  setMode(modeOrder[i]);
}

document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode)));
document.getElementById('prevBtn').addEventListener('click',()=>step(-1));
document.getElementById('nextBtn').addEventListener('click',()=>step(1));
document.getElementById('search').addEventListener('keydown',e=>{if(e.key==='Enter')setMode('can')});
document.getElementById('fullscreenBtn').addEventListener('click',()=>{
  if(!document.fullscreenElement)document.documentElement.requestFullscreen?.();
  else document.exitFullscreen?.();
});
document.addEventListener('keydown',e=>{
  if(e.key==='ArrowRight')step(1);
  if(e.key==='ArrowLeft')step(-1);
  if(e.key.toLowerCase()==='f'){
    document.body.classList.toggle('presentation');
  }
});
nodes.forEach(n=>n.addEventListener('click',()=>{
  if(n.dataset.id==='cpf')setMode('can');
  if(n.dataset.id==='customer-api')setMode('breaks');
  if(n.dataset.id==='legacy-service')setMode('hidden');
}));
window.addEventListener('resize',()=>{draw();setMode(currentMode)});

draw();
setMode('overview');