'use strict';
// This extension is included only in a locally generated contract-case workspace.
(() => {
  const isCase=()=>data?.provenance?.kind==='public_contract_case';
  const facts=()=>data.provenance.facts;
  function caseReport(){
    const f=facts(),snapshot=EGGraph.snapshot();
    const lines=['# EvidentGraph — '+f.title,'','Caso público documental. Não é execução de clientes nem aprovação de publicação.','',
      `Operação: ${f.method} ${f.endpoint}; resposta ${f.response_status}.`,
      `Versões: ${f.sources[0].version} → ${f.sources[1].version}.`,
      `Campo: ${f.field.join('.')}. Declarado antes; não declarado depois neste objeto.`,
      `Obrigatório no contrato anterior: ${f.previous.required?'sim':'não'}.`,
      'Consumidores e responsáveis por integrações: UNKNOWN. Execução: NOT_VERIFIED.',
      'A ausência de consumidores no material não significa ausência de uso.','',
      '## Orientação documental',f.migration_note,
      `Caminho indicado: ${f.replacement_field.join('.')||'não informado'}. Sua presença foi conferida; equivalência não foi inferida.`,
      `Documentação: ${f.documentation_url}`,'','## Fontes'];
    for(const source of f.sources)lines.push(`- ${source.id}: ${source.url}`,`  Versão ${source.version}; SHA-256 ${source.sha256}; cópia local ${source.file}.`);
    lines.push('','## Recorte visível',`Ativos: ${snapshot.ids.length}. Relações: ${snapshot.edgeIds.length}.`);
    for(const id of snapshot.edgeIds){const r=relations[id];lines.push(`- ${r.source} — ${r.kind} → ${r.target}; fontes: ${r.evidence_ids.join(', ')}.`);}
    lines.push('','## O que falta para avaliar impacto','Identificar sistemas reais que usam a resposta, a versão de API adotada e o uso do campo; obter um teste pertinente e o responsável.','As relações CONTAINS descrevem a estrutura de cada contrato, sem chamadas ou conexões operacionais entre versões.','Conferência documental limitada à presença do campo selecionado em JSON OpenAPI autocontido. Não executa oasdiff ou chamadas HTTP à API.');
    if(data.provenance.consumer_demo&&window.EGConsumerDemo)lines.push('',EGConsumerDemo.report());
    else lines.push('Nenhum código de consumidor foi executado neste espaço documental.');
    return lines.join('\n')+'\n';
  }
  const originalDetails=openDetails;
  openDetails=function(id,inventory=false){
    originalDetails(id,inventory);
    if(!isCase()||!assets[id]||!$('detailDialog').open)return;
    const heading=Array.from($('detailBody').querySelectorAll('h3')).find(h=>h.textContent==='Análises disponíveis');
    if(heading){
      heading.textContent='Nesta comparação';
      heading.nextElementSibling.innerHTML=`<button class="secondary" data-case-return>Voltar à comparação ${esc(result.change.id)}</button>`;
    }
    const refs=(assets[id].evidence_ids||[]).map(key=>evidences[key]).filter(Boolean);
    const simulated=assets[id].material_kind==='simulated_consumer';
    $('detailBody').insertAdjacentHTML('beforeend',simulated?'<h3>Execução do exemplo simulado</h3><p>Código próprio executado localmente em recortes fictícios. Não identifica uso real da Stripe.</p>'+refs.map(evidenceMarkup).join(''):'<h3>Contrato e origem</h3><p>O registro descreve o contrato nesta versão. Não comprova consumo ou execução.</p>'+refs.map(evidenceMarkup).join(''));
  };
  const originalReport=report;
  report=()=>isCase()?caseReport():originalReport();
  function renderCaseInspector(){
    if(!isCase())return;
    const explanation=document.querySelector('.inspector-impact p');
    if(explanation)explanation.textContent='Consumidores desconhecidos. Consulte o contrato e a orientação documental antes de investigar uma integração.';
  }
  function showComparison(){
    if(!isCase())return;
    if($('detailDialog').open)$('detailDialog').close();
    setView('analysis');
    const title=$('consumerDemoTitle')||$('contractComparisonTitle');
    if(title){title.tabIndex=-1;title.focus({preventScroll:true});title.scrollIntoView({block:'start',behavior:'auto'});}
  }
  function renderCase(){
    if(!isCase())return;
    const f=facts();
    document.body.classList.add('contract-case');
    $('changeDescription').textContent=`${f.method} ${f.endpoint}: o contrato posterior deixou de declarar ${f.field.join('.')}.`;
    $('analysisState').textContent='Comparação documental aberta. O impacto em consumidores permanece desconhecido.';
    $('changeMeta').innerHTML=`<div><dt>Versão anterior</dt><dd>${esc(f.sources[0].version)}</dd></div><div><dt>Versão posterior</dt><dd>${esc(f.sources[1].version)}</dd></div><div><dt>Escopo</dt><dd>Resposta ${esc(f.response_status)} · application/json</dd></div><div><dt>Observação de execução</dt><dd>Não realizada</dd></div>`;
    $('conclusionTitle').textContent='Mudança confirmada no contrato; impacto ainda desconhecido';
    $('conclusionText').textContent='O campo estava documentado na versão anterior e não aparece no mesmo objeto na versão posterior. Precisamos identificar quem o utiliza para avaliar consequências.';
    $('scopeNote').textContent=`O campo era ${f.previous.required?'obrigatório':'opcional'} no contrato anterior. Ausência de consumidores neste material não significa ausência de uso.`;
    $('summaryLine').textContent='Consumidores ainda não identificados · nenhum teste de integração executado.';
    $('metrics').hidden=true;document.querySelector('#analysisResult .table-card').hidden=true;
    $('exportBtn').disabled=false;
    document.querySelector('#analysisView .page-head p').textContent='Confira a alteração documentada e o que falta para investigar seus consumidores.';
    document.querySelector('#analysisView .change-details summary').textContent='Versões e escopo documental';
    document.querySelector('#analysisResult .bottom-note').innerHTML='<strong>Próximo passo</strong><p>Identificar uma integração que use essa resposta, sua versão da API e o uso do campo. Só então avaliar um teste e o responsável pela revisão.</p>';
    if(!$('contractComparison')){
      const section=document.createElement('section');section.id='contractComparison';section.className='contract-comparison';section.setAttribute('aria-label','Antes e depois do contrato');
      section.innerHTML=`<h2 id="contractComparisonTitle">Comparação dos contratos</h2><div class="contract-versions"><article><h3>Antes</h3><p>${esc(f.sources[0].version)}</p><code>${esc(f.field.join('.'))}</code><p>Campo declarado · ${f.previous.required?'obrigatório':'opcional'}</p><button class="secondary" data-contract-detail="response-before">Examinar contrato anterior</button></article><article><h3>Depois</h3><p>${esc(f.sources[1].version)}</p><code>${esc(f.replacement_field.join('.')||'Sem caminho alternativo informado')}</code><p>O campo original não está declarado no mesmo objeto.</p><button class="secondary" data-contract-detail="response-after">Examinar contrato posterior</button></article></div><p class="case-migration">${esc(f.migration_note)}</p><details><summary>Fontes e verificação dos arquivos</summary><p><a href="${esc(f.documentation_url)}" target="_blank" rel="noopener noreferrer">Orientação publicada pelo fornecedor ↗</a></p>${f.sources.map(s=>`<p><strong>${esc(s.version)}</strong> · <a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">Fonte original ↗</a> · <a href="${esc(s.file)}" download>Cópia preservada</a><br><small>SHA-256: <code>${esc(s.sha256)}</code></small></p>`).join('')}<p>A conferência verifica o campo selecionado nos contratos. Não executa a API nem determina automaticamente os consumidores.</p></details>`;
      document.querySelector('#analysisResult .conclusion').after(section);
      section.addEventListener('click',e=>{const b=e.target.closest('[data-contract-detail]');if(b)openDetails(b.dataset.contractDetail,true);});
    }
  }
  document.addEventListener('eg:ready',()=>{
    const select=$('workspaceSource');select.value=isCase()?'case':'aurora';
    select.addEventListener('change',()=>{const url=new URL(location.href);for(const key of [...url.searchParams.keys()])if(key.startsWith('eg_'))url.searchParams.delete(key);url.searchParams.set('source',select.value);url.hash='';location.assign(url.href);});
    if(!isCase())return;
    const f=facts();
    $('contextName').textContent='Caso público';
    document.querySelector('.company').innerHTML='Contratos de API<small>Caso público documentado</small>';
    document.querySelector('.side-foot .workspace-label').textContent='REVISÃO DOCUMENTAL';
    document.querySelector('.catalog-totals small').textContent='na estrutura deste caso';
    document.querySelector('.footer>span').textContent='EvidentGraph · caso público';
    $('datasetLabel').textContent='Fontes preservadas em '+date(f.captured_at);
    $('graphScope').querySelector('[value="all"]').textContent='Caso completo';
    $('graphTechnical').closest('label').lastChild.textContent=' Campos e identidades';
    $('graphReset').textContent='Focar contrato anterior';
    $('graphReview').textContent='← Revisar esta mudança';
    $('contractCaseNotice').hidden=false;
    $('contractCaseNotice').innerHTML=`<div><strong>${esc(f.title)}</strong><p>Contratos públicos reais. Consumidores e execução ainda desconhecidos.</p></div><button id="reviewPublicCase" class="primary">Ver comparação →</button>`;
    $('reviewPublicCase').addEventListener('click',showComparison);
    $('detailBody').addEventListener('click',e=>{if(e.target.closest('[data-case-return]'))showComparison();});
    $('analysisToGraph').addEventListener('click',()=>{$('graphScope').value='all';$('graphTechnical').checked=true;EGGraph.repaint();});
    document.querySelector('#aboutDialog .dialog-body').innerHTML='<p>Este espaço apresenta contratos públicos preservados e uma conferência local do campo selecionado. As relações do mapa representam campos documentados em cada versão, sem conectar as versões como fluxo operacional.</p><p>Nenhum consumidor foi identificado, nenhuma chamada à API foi executada e nenhum responsável de integração foi confirmado. UNKNOWN não significa ausência de risco.</p><p>O caminho alternativo foi indicado na descrição do caso e conferido no contrato posterior. Isso não comprova equivalência semântica ou sucesso de migração. Grupo Aurora permanece disponível como conjunto fictício separado.</p>';
    renderCase();renderCaseInspector();
  });
  document.addEventListener('eg:analysis',renderCase);
  document.addEventListener('eg:graphinspect',renderCaseInspector);
  window.EGContractCase={report:caseReport};
})();
