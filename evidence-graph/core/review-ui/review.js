'use strict';
/* Presentation of a historical, versioned experiment. Clicking never runs tests. */
(() => {
  let showTests=false;
  const current=()=>data?.provenance?.kind==='l7_review';
  const inference=p=>p.predicted_exception==='YES'?'Exceção prevista no recorte':p.predicted_exception==='NO'?'Sem exceção prevista no recorte':'Inferência inconclusiva';
  const execution=t=>({FAILED:'Exceção observada no teste',COMPLETED:'Concluiu sem exceção',BASELINE_NOT_ESTABLISHED:'Comparação não estabelecida'})[t.execution];
  const business=t=>({VIOLATED:'Requisito violado no teste',MET:'Requisito atendido no teste',NOT_EVALUATED:'Requisito não avaliado'})[t.business];
  const signal=p=>p.observed_field_access==='YES'?'Leitura do campo observada':p.declared_requirement==='YES'?'Campo exigido no manifesto':'Indício insuficiente neste recorte';
  function stages(r, compact=false) {
    const {prediction:p,tests:t}=r.review;
    return `<div class="evidence-stages ${compact?'compact':''}"><section><small>1 · INDÍCIO</small><strong>${esc(signal(p))}</strong>${compact?'':'<p>Uma dependência aponta o que investigar; não confirma uma falha.</p>'}</section><section><small>2 · INFERÊNCIA</small><strong>${esc(inference(p))}</strong>${compact?'':'<p>Sob as hipóteses do código e da resposta analisados. Não é garantia de funcionamento.</p>'}</section><section class="${showTests&&t.business==='VIOLATED'?'business-risk':''}"><small>3 · TESTE REGISTRADO</small><strong>${showTests?esc(execution(t)):'Resultado ainda não exibido'}</strong>${showTests?`<span>${esc(business(t))}</span>`:'<span>Consultar não executa um novo teste.</span>'}</section></div>`;
  }
  function inspect() {
    if(!current())return;
    const r=result.consumers.find(r=>r.consumer===EGGraph.snapshot().selected);
    if(!r)return;
    const box=$('graphInspector').querySelector('.inspector-impact');
    if(box)box.innerHTML=stages(r,true)+`<div class="next-action"><small>PRÓXIMA VERIFICAÇÃO</small><p>${esc(r.next_step)}</p><button class="row-open" data-inspect="${esc(r.consumer)}">Entender as evidências →</button></div>`;
  }
  function evidence(e) {return `<details class="ev"><summary><strong>${esc(e.title)}</strong><br><small>${esc(e.reference)}</small></summary><pre>${esc(JSON.stringify(e.details,null,2))}</pre></details>`;}
  function detail(id, old, fromInventory) {
    const r=result.consumers.find(x=>x.consumer===id);if(!r){old(id,fromInventory);return;}
    const {prediction:p, tests:t}=r.review;
    $('detailTitle').textContent=r.name;$('detailKind').textContent='REVISÃO DA MUDANÇA · '+r.review.case_id;
    $('detailBody').innerHTML=stages(r)+`<p class="local-note">Fonte: execução histórica de laboratório. A inferência não recebeu os resultados posteriores. A associação entre código e consumidor é configurada, não descoberta em uma empresa.</p>
      ${p.declaration_source_disagreement?'<p class="review-conflict"><strong>Divergência entre manifesto e código.</strong> As fontes não concordam; o sistema preserva a divergência para revisão.</p>':''}
      <h3>Hipóteses e limites da inferência</h3><p>Python restrito; dicionário exato; campos string obrigatórios; sem efeitos externos. Formas não reconhecidas permanecem inconclusivas.</p><p><strong>Motivo registrado:</strong> <code>${esc(p.prediction_basis.basis)}</code>.</p>
      <h3>O que fazer agora</h3><p>${esc(r.next_step)}</p><p><strong>Responsável:</strong> ${esc(team(r.owner))}. Equipe e processo de negócio não foram descobertos nesta captura.</p>
      ${showTests?`<h3>O que o teste verificou</h3><p>${esc(execution(t))}. ${esc(business(t))}.</p>${t.requirement?`<p><strong>Requisito informado ao avaliador:</strong> ${esc(t.requirement)}.</p>`:'<p>Não há avaliação de requisito de negócio neste conjunto.</p>'}<p>${t.input_cases} caso(s) de entrada. O resultado não se estende a outros inputs ou versões.</p>`:''}
      <h3>Evidências anteriores à mudança</h3>${r.review.pre_evidence_ids.map(id=>evidence(evidences[id])).join('')}
      ${showTests?'<h3>Referência de teste posterior — não usada na previsão</h3>'+r.review.test_evidence_ids.map(id=>evidence(evidences[id])).join(''):''}
      <h3>Registro de verificação</h3><label class="review-label"><input type="checkbox" data-check="${esc(id)}" ${check(id).done?'checked':''}><span>${check(id).done?'Anotada':'Pendente'}</span></label><label for="reviewNote">Notas locais</label><textarea id="reviewNote" data-note="${esc(id)}" maxlength="2000">${esc(check(id).note)}</textarea><p class="local-note">A anotação não altera a inferência ou o teste. Exporte para compartilhar; nada é enviado à equipe.</p>`;
    $('detailDialog').showModal();$('closeDetail').focus();
  }
  function decorate() {
    if(!current())return;
    for(const b of $('consumerRows').querySelectorAll('[data-detail]')){
      const r=result.consumers.find(x=>x.consumer===b.dataset.detail);
      if(r)b.closest('tr').children[1].innerHTML=stages(r,true);
    }
    // Counters keep the same filtering keys; labels explain they are indicators, not verdicts.
    const labels={'':'Todos','INCOMPATIBILITY':'Contrato','POSSIBLE':'Indício de impacto','INCONCLUSIVE':'Indício insuficiente','NO_INCOMPATIBILITY':'Contrato sem divergência'};
    $('metrics').querySelectorAll('[data-impact]').forEach(b=>b.querySelector('span').textContent=labels[b.dataset.impact]);
    $('conclusionTitle').textContent='O que sabemos — e o que ainda precisa de teste';
    $('conclusionText').textContent='Separe o indício da previsão e do resultado executado. Ausência de exceção não garante que o requisito de negócio foi atendido.';
  }
  function exportReview() {
    const rows=visibleRows(),p=data.provenance;
    const lines=['# EvidentGraph — revisão por evidências','',
      '**Captura histórica de laboratório. Consultar resultados não executa novos testes.**','',
      `Conjunto: ${p.cohort}. Hash do conjunto: ${p.source_sha256}.`,
      `Exportados: ${rows.length} de ${result.consumers.length} consumidores. Testes posteriores incluídos: ${showTests?'sim':'não'}.`,
      `Filtros: busca=${md($('search').value)}; indício=${impactFilter||'todos'}; equipe=${$('ownerFilter').value||'todas'}; uso=${$('activityFilter').value||'todos'}.`,
      '', '| Consumidor | Indício | Inferência | Teste de execução | Requisito de negócio |','|---|---|---|---|---|'];
    for(const r of rows){const {prediction:p,tests:t}=r.review;lines.push(`| ${md(r.name)} | ${signal(p)} | ${inference(p)} | ${showTests?execution(t):'Não incluído'} | ${showTests?business(t):'Não incluído'} |`);}
    for(const r of rows){const p=r.review.prediction;lines.push('',`## ${md(r.name)}`,
        `Responsável: ${md(team(r.owner))}. Próximo passo: ${md(r.next_step)}`,
        `Inferência: ${inference(p)}. Base: ${p.prediction_basis.basis}.`,
        'Hipóteses: subconjunto restrito de Python, dicionário exato, strings obrigatórias, sem efeitos externos.',
        `Divergência manifesto/código: ${p.declaration_source_disagreement?'sim':'não identificada'}.`,
        'Confirmação disponível ao preditor: NOT_TESTED. Correção semântica pelo preditor: UNKNOWN.',
        `Verificação manual: ${check(r.consumer).done?'anotada; não resolve a mudança':'pendente'}. Nota: ${md(check(r.consumer).note)||'nenhuma'}.`);
      if(showTests&&r.review.tests.requirement)lines.push('Requisito informado ao avaliador: '+md(r.review.tests.requirement));
      const refs=[...r.review.pre_evidence_ids,...(showTests?r.review.test_evidence_ids:[])];
      refs.forEach(id=>lines.push('- '+evidences[id].title+': '+evidences[id].reference));
    }
    lines.push('','## Limites','Casos do mesmo autor; não é validação independente, aprovação ou previsão geral de falhas. Relações do grafo são mapeamentos do experimento. Os testes cobrem apenas entradas preparadas.');
    return lines.join('\n')+'\n';
  }
  document.addEventListener('eg:ready',()=>{
    const select=$('workspaceSource'),source=window.EG_SOURCE;
    select.value=source;const url=new URL(location.href);url.searchParams.set('source',source);
    try{history.replaceState(null,'',url.href);}catch{/* Some offline viewers disallow history. */}
    const notice=document.createElement('p');notice.id='storageNotice';notice.className='capture-notice';notice.setAttribute('role','status');
    notice.textContent='Notas temporárias: armazenamento indisponível. Exporte antes de trocar a fonte ou recarregar.';
    $('captureNotice').after(notice);notice.hidden=persist;
    const save=store;store=function(id,patch){save(id,patch);notice.hidden=persist;};
    select.addEventListener('change',()=>{
      if(select.value===source)return;
      if(!persist&&Object.values(checks).some(x=>x.done||x.note)&&!confirm('Notas temporárias. Trocar sem exportar?')){select.value=source;return;}
      const target=new URL(location.href);target.searchParams.set('source',select.value);target.hash='';
      select.disabled=true;select.setAttribute('aria-busy','true');location.assign(target.href);
    });
    // Restore interaction when the page is recovered from the back/forward cache.
    window.addEventListener('pageshow',()=>{if(window.EG_WORKSPACE_READY){select.disabled=false;select.value=source;}});
    if(!current())return;
    const name=source==='review'?'Aurora Revisão':'Aurora Validação';
    document.title='EvidentGraph · '+name;$('contextName').textContent=name;
    document.querySelector('.company').innerHTML=esc(name)+'<small>Revisão por evidências</small>';
    $('workspaceEnvironment').textContent='Laboratório';$('datasetLabel').textContent='Referência: '+date(data.clock);
    document.querySelector('.footer > span').textContent='EvidentGraph · '+name;
    document.querySelector('.catalog-totals small').textContent='neste conjunto separado';
    IMPACT.POSSIBLE=['Indício de impacto','warning','A dependência aponta uma verificação; não confirma falha.'];
    IMPACT.INCONCLUSIVE=['Indício insuficiente','neutral','Informação insuficiente não demonstra ausência de impacto.'];
    ACTIVITY.OBSERVED='Chamada anterior observada';ACTIVITY.UNKNOWN='Uso anterior não confirmado';
    const bar=document.createElement('div');bar.className='review-mode';bar.innerHTML='<div><strong>Antes de concluir, confira o nível da evidência</strong><p>Indício → inferência → teste registrado. Cada resposta tem um escopo.</p></div><label><input type="checkbox" id="showRecordedTests"> Mostrar testes registrados</label>';
    $('captureNotice').before(bar);
    $('showRecordedTests').addEventListener('change',()=>{showTests=$('showRecordedTests').checked;decorate();inspect();if($('detailDialog').open){const id=$('reviewNote')?.dataset.note;if(id){$('detailDialog').close();openDetails(id);}}});
    const previous=openDetails;openDetails=function(id,fromInventory=false){detail(id,previous,fromInventory);};
    report=exportReview;evidenceMarkup=evidence;
    document.querySelector('#aboutDialog .dialog-body').innerHTML='<p>As fontes Aurora Revisão e Aurora Validação apresentam capturas do experimento L6-B, separadas do Grupo Aurora de 240 ativos. Os nomes são rótulos fictícios. Equipes, processos e criticidade não foram descobertos.</p><p>A inferência foi recalculada a partir das entradas anteriores. Os resultados posteriores vêm de referências de teste separadas. Mostrar esses resultados não executa código nem modifica previsões.</p><p>As relações de consumo de resposta são definidas pelo experimento; não representam descoberta automática de chamadas HTTP. Os casos e as regras são do mesmo autor. A análise restrita não foi promovida a um detector geral.</p><p>Notas locais pertencem a esta captura e não alteram evidências. Não há conexão a empresas ou monitoramento contínuo.</p>';
    document.querySelector('#consumerRows').closest('table').querySelectorAll('th')[1].textContent='Níveis de evidência';
    document.querySelector('.bottom-note p').textContent='Indício, inferência e teste não são equivalentes. Consultar o resultado posterior não transforma uma previsão em prova anterior nem autoriza uma publicação.';
    renderConsumers();inspect();
  });
  document.addEventListener('eg:filtered',decorate);
  document.addEventListener('eg:graphinspect',inspect);
})();
