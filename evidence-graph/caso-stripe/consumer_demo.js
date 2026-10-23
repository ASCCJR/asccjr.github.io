'use strict';
// Shows recorded, locally executed examples; switching cards never reruns Python.
(() => {
  const demo=()=>data?.provenance?.consumer_demo;
  const labels={LINKED:'Assinatura associada',NO_SUBSCRIPTION:'Sem assinatura',REVIEW:'Pedir revisão'};
  let selected='subscription-id',ready=false,invalidExample=false;
  const outcome=value=>value?`${labels[value.status]||value.status}${value.subscription_id?' · '+value.subscription_id:''}`:'Sem resultado';
  function report(){
    const d=demo();if(!d)return '';
    const lines=['## Consumidor simulado: execução local registrada',d.business_expectation,
      `Execução: ${d.executed_at}. Escopo: ${d.execution_scope}.`,
      'Recortes e expectativas preparados para esta demonstração; nenhuma chamada à Stripe ou consumidor real identificado.',
      'DEMO_READS liga o código do exemplo ao campo que ele lê; não representa telemetria nem descoberta automática.',
      '','| Cenário | Código / contrato | Esperado | Obtido | Conferência |',
      '|---|---|---|---|---|'];
    for(const r of d.runs)lines.push(`| ${r.label} | ${r.implementation==='legacy'?'Antigo':'Adaptado'} / ${r.stage==='before'?'anterior':'novo'} | ${outcome(r.expected)} | ${r.exception?'Exceção: '+r.exception.type:outcome(r.actual)} | ${r.matches_expectation?'Confere':'Diverge'} |`);
    lines.push('','Resultados completos: demo/result.json. Código e entradas:');
    for(const f of d.files)lines.push(`- ${f.file}; SHA-256 ${f.sha256}.`);
    lines.push('','Limites:',...d.limitations.map(t=>'- '+t),'Consumidores reais: UNKNOWN. Execução de integrações reais: NOT_VERIFIED.');
    return lines.join('\n');
  }
  function renderSelection(){
    if(!$('demoCaseSelect'))return;
    $('demoCaseSelect').value=selected;
    $('demoLinkStatus').textContent=invalidExample?'O exemplo indicado no link não foi encontrado. Mostrando “Fatura vinculada a uma assinatura”.':'';
    const d=demo(),host=$('demoExample');if(!d||!host)return;
    const rows=d.runs.filter(r=>r.case_id===selected);
    host.classList.toggle('two',rows.length===2);
    host.innerHTML=rows.map(r=>`<article class="demo-run ${r.matches_expectation?'matches':'differs'}"><h4>${r.implementation==='legacy'?'Código antigo':'Código adaptado'}<small>${r.stage==='before'?'Contrato anterior':'Contrato novo'}</small></h4><p class="demo-outcome">${esc(r.exception?'Exceção: '+r.exception.type:outcome(r.actual))}</p><p><strong>${r.matches_expectation?'Confere com a expectativa':'Diverge da expectativa'}</strong></p><p>Esperado: ${esc(outcome(r.expected))}.</p><p>${r.exception?'A execução lançou uma exceção.':'A execução terminou sem exceção.'}</p><details><summary>Ver entrada e resultado</summary><pre>${esc(JSON.stringify({entrada:r.input,esperado:r.expected,obtido:r.actual,excecao:r.exception},null,2))}</pre></details></article>`).join('');
    $('demoCategory').textContent=rows[0]?.category==='robustness'?'Caso de robustez: entrada incompleta ou fora do escopo; o resultado esperado é pedir revisão.':'Recorte sintético dos campos selecionados. Não é uma resposta completa coletada da API.';
    $('demoSelectionStatus').textContent=`Cenário exibido: ${rows[0]?.label||''}. ${rows.length} execuções registradas.`;
  }
  function render(){
    const d=demo();if(!ready||!d)return;
    document.body.classList.add('has-consumer-demo');
    $('workspaceEnvironment').textContent='Contratos públicos + consumidor simulado';
    $('contextName').textContent='Caso + simulação';
    $('contractCaseNotice').querySelector('p').textContent='Contratos públicos reais e código de exemplo executado localmente. Consumidores reais continuam desconhecidos.';
    $('summaryLine').textContent='Exemplo local executado · nenhum consumidor real identificado';
    const failure=d.runs.find(r=>r.case_id==='subscription-id'&&r.stage==='after'&&r.implementation==='legacy');
    const corrected=d.runs.find(r=>r.case_id==='subscription-id'&&r.stage==='after'&&r.implementation==='migrated');
    $('conclusionTitle').textContent=failure&&!failure.matches_expectation&&!failure.exception?'O código antigo perde a associação no exemplo':'Resultado do consumidor simulado disponível';
    $('conclusionText').textContent=`Com os campos da versão nova, o leitor antigo devolveu “${outcome(failure?.actual)}”. ${corrected?.matches_expectation?'O leitor adaptado preservou a associação esperada.':'O resultado do leitor adaptado precisa de revisão.'} Esses resultados são do nosso exemplo; o impacto em integrações reais permanece desconhecido.`;
    $('analysisState').textContent='Comparação e execução do exemplo disponíveis. Os resultados abaixo já foram registrados localmente.';
    const observation=[...$('changeMeta').querySelectorAll('div')].find(el=>el.querySelector('dt')?.textContent==='Observação de execução');
    if(observation){observation.querySelector('dt').textContent='Execução da integração real';observation.querySelector('dd').textContent='Não realizada';}
    document.querySelector('#analysisView .page-head p').textContent='Compare o contrato e veja a consequência em um consumidor simulado, com entradas e resultados inspecionáveis.';
    document.querySelector('#analysisResult .bottom-note').innerHTML='<strong>Próximo passo</strong><p>Revisar estas expectativas com alguém que integra APIs e, quando houver acesso, repetir o procedimento com uma integração real. O resultado do exemplo não aprova uma migração em produção.</p>';
    if(!$('consumerDemo')){
      const section=document.createElement('section');section.id='consumerDemo';section.className='consumer-demo';section.setAttribute('aria-labelledby','consumerDemoTitle');
      const cases=[...new Map(d.runs.map(r=>[r.case_id,r])).values()];
      section.innerHTML=`<header><span class="demo-tag">CONSUMIDOR SIMULADO</span><h3 id="consumerDemoTitle">O que acontece com a associação da fatura?</h3><p>${esc(d.business_expectation)}</p></header><p>Executamos nosso código com recortes fictícios das duas versões. Os cartões mostram resultados gravados; trocar o cenário não faz chamadas à Stripe.</p><label for="demoCaseSelect">Exemplo para conferir</label><select id="demoCaseSelect">${cases.map(r=>`<option value="${esc(r.case_id)}">${esc(r.label)}</option>`).join('')}</select><p id="demoCategory" class="demo-scope"></p><div id="demoExample" class="demo-results"></div><p id="demoSelectionStatus" class="sr-only" role="status"></p><p class="demo-learning"><strong>Terminar sem erro não basta.</strong> É preciso comparar a saída com a expectativa da tarefa. Informação ausente deve continuar pedindo revisão.</p><div class="demo-actions"><button class="secondary" data-demo-detail="demo-legacy">Examinar leitor antigo</button><button class="secondary" data-demo-detail="demo-migrated">Examinar leitor adaptado</button></div><details class="demo-evidence"><summary>Resultados completos, código e limites</summary><p>Execução registrada em ${esc(date(d.executed_at))}. Foram ${d.runs.length} execuções sobre ${cases.length} cenários preparados, incluindo casos de robustez. Não são testes com clientes.</p><ul>${d.summary.map(s=>`<li>${s.implementation==='legacy'?'Antigo':'Adaptado'} / ${s.stage==='before'?'contrato anterior':'contrato novo'}: ${s.matched} de ${s.total} resultados conferem; ${s.mismatched} divergem; ${s.exceptions} exceções.</li>`).join('')}</ul><p><a href="demo/result.json" download>Baixar resultados completos</a> · <a href="demo/consumer_demo.py" download>Baixar código do exemplo</a> · <a href="demo/consumer_demo_cases.json" download>Baixar recortes e expectativas</a></p><p>Reproduzir a execução requer o projeto e os contratos preservados; instruções no README do adaptador. O arquivo de código isolado não é um aplicativo.</p><ul>${d.limitations.map(t=>`<li>${esc(t)}</li>`).join('')}</ul><p>O leitor antigo já confunde um campo omitido com ausência de assinatura no contrato anterior. Essa limitação também aparece nos resultados.</p></details>`;
      $('contractComparison').before(section);
      const status=document.createElement('p');status.id='demoLinkStatus';status.className='demo-scope';status.setAttribute('role','status');$('demoCaseSelect').after(status);
      $('demoCaseSelect').addEventListener('change',e=>{selected=e.target.value;invalidExample=false;renderSelection();emit('example');});
      section.addEventListener('click',e=>{const b=e.target.closest('[data-demo-detail]');if(b)openDetails(b.dataset.demoDetail,true);});
      renderSelection();
    }
    const about=document.querySelector('#aboutDialog .dialog-body');
    if(!about.querySelector('[data-demo-about]'))about.innerHTML='<p data-demo-about><strong>Contratos públicos e consumidor simulado.</strong> Este espaço combina quatro ativos documentais e duas implementações de exemplo. As relações “Lê no exemplo” foram declaradas para esse código, sem coletor ou chamada HTTP. O código foi executado localmente em recortes fictícios; consumidores reais permanecem UNKNOWN, com execução NOT_VERIFIED.</p><p>A comparação documental e os testes do exemplo têm escopos diferentes. Grupo Aurora continua separado. O navegador mostra os resultados preservados; não reexecuta o teste.</p>';
  }
  function inspector(){
    if(!demo())return;
    const id=window.EGGraph?.snapshot().selected,asset=assets[id];
    let p=document.querySelector('.inspector-impact p');
    if(!p){const section=document.createElement('div');section.className='inspector-impact';section.innerHTML='<p></p>';document.querySelector('.inspector-actions').before(section);p=section.querySelector('p');}
    if(p)p.textContent=asset?.material_kind==='simulated_consumer'?'Leitor criado para demonstração. Seus resultados locais ficam nos detalhes; não representa uma integração real.':'Documento público. Os vínculos com leitores simulados explicam o exemplo, sem comprovar uso real.';
  }
  window.EGConsumerDemo={report,
    selection:()=>demo()?selected:'',
    restore:value=>{
      const ids=new Set((demo()?.runs||[]).map(r=>r.case_id));
      invalidExample=Boolean(value)&&ids.size>0&&!ids.has(value);
      selected=ids.has(value)?value:'subscription-id';
      if(ready&&demo())renderSelection();
    }
  };
  document.addEventListener('eg:ready',()=>{ready=true;render();inspector();});
  document.addEventListener('eg:analysis',render);
  document.addEventListener('eg:view',render);
  document.addEventListener('eg:graphinspect',inspector);
})();
