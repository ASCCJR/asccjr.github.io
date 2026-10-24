'use strict';
/* Optional presentation adapter. Never combines datasets or collects telemetry in the browser. */
(() => {
  const isLab = () => data?.provenance?.kind === 'l1_capture';
  const labels = {FAIL_OBSERVED_IN_LAB:'Falhou no teste executado',
    PASS_IN_EXECUTED_CHECK:'Passou no teste executado', NOT_VERIFIED:'Não verificado'};
  const state = r => `<span class="badge ${r.lab_regression==='FAIL_OBSERVED_IN_LAB'?'danger':'neutral'}">${esc(labels[r.lab_regression])}</span>`;
  function phases(r) {
    return `<section class="lab-result"><h3>Teste do consumidor após a mudança (v2)</h3>${state(r)}<p>Uma verificação executada, não uma garantia de funcionamento completo.</p><div class="detail-grid">${['v1','v2'].map(v=>`<div><small>${v==='v1'?'ANTES · v1':'DEPOIS · v2'}</small>${r.lab_phases[v].usage==='OBSERVED'?'Chamada correlacionada':'Uso não confirmado'}<p>Verificações: ${esc(r.lab_phases[v].checks.join(', ')||'não executadas/confirmadas')}</p><code>${esc(r.lab_phases[v].trace_ids.join(' · ')||'Sem trace correlacionado')}</code></div>`).join('')}</div></section>`;
  }
  function decorateRows() {
    if(!isLab())return;
    for(const button of $('consumerRows').querySelectorAll('[data-detail]')) {
      const r=result.consumers.find(r=>r.consumer===button.dataset.detail);
      if(!r)continue;
      const cell=button.closest('tr').children[1];
      if(!cell.querySelector('.lab-test'))cell.insertAdjacentHTML('beforeend',`<div class="lab-test"><small>TESTE APÓS · v2</small>${state(r)}</div>`);
    }
  }
  function inspector() {
    if(!isLab())return;
    const a=assets[EGGraph.snapshot().selected];
    const r=result.consumers.find(r=>r.consumer===a?.id);
    const box=$('graphInspector');
    if(r&&!box.querySelector('.lab-inspector'))box.insertAdjacentHTML('beforeend',`<section class="lab-inspector"><strong>Resultado executado · v2</strong><p>${state(r)}</p><small>Contrato e falha observada são avaliações distintas.</small></section>`);
  }
  function labReport() {
    const p=data.provenance, rows=visibleRows();
    const lines=['# EvidentGraph — revisão com evidências do laboratório','',
      '**Aurora Lab · dados de negócio fictícios; telemetria capturada de execução local. Não é produção nem monitoramento ao vivo.**','',
      `Captura: ${p.started_at} a ${p.finished_at}.`, `SHA-256 do run.json: ${p.source_sha256}.`,
      `Adaptador: ${p.adapter_version}. Dataset: ${data.dataset_version}.`,
      `Mudança: remover ${md(result.change.field)} da API de clientes (v1 → v2).`,
      `Filtros: busca=${md($('search').value)||'nenhuma'}; impacto=${impactFilter||'todos'}; equipe=${$('ownerFilter').value||'todas'}; uso anterior=${$('activityFilter').value||'todos'}.`,
      `Consumidores exportados: ${rows.length} de ${result.consumers.length}.`, '',
      '| Consumidor | Contrato | Uso antes · v1 | Teste após · v2 | Responsável |', '|---|---|---|---|---|'];
    for(const r of rows)lines.push(`| ${md(r.name)} | ${IMPACT[r.impact][0]} | ${ACTIVITY[r.activity]} | ${labels[r.lab_regression]} | ${md(team(r.owner))} |`);
    for(const r of rows){
      lines.push('',`## ${md(r.name)}`,`Próximo passo: ${md(r.next_step)}.`,
        `Anotação do usuário: ${check(r.consumer).done?'registrada; não altera o teste':'pendente'}.`,
        `Nota local: ${md(check(r.consumer).note)||'sem anotação'}.`);
      for(const v of ['v1','v2'])lines.push(`Traces ${v}: ${r.lab_phases[v].trace_ids.join(', ')||'nenhum correlacionado'}.`);
      for(const id of r.evidence_ids){const e=evidences[id];lines.push(`- ${id} · ${e.family} · ${e.reference} · versão ${e.target_version}.`);}
    }
    lines.push('','## Limites',...p.limitations.map(x=>'- '+x),
      '- Requisitos dos consumidores são declarados e compartilhados pelo comparador e pelo teste; não é benchmark independente.',
      '- Processos e criticidade não foram coletados. Nada é enviado aos responsáveis.');
    return lines.join('\n')+'\n';
  }
  document.addEventListener('eg:ready',()=>{
    const select=$('workspaceSource');select.value=isLab()?'lab':'aurora';
    // Keep the data source separate from page anchors; retain legacy #aurora links.
    const canonical = new URL(location.href);
    canonical.searchParams.set('source', select.value);
    if (['#lab', '#aurora'].includes(canonical.hash)) canonical.hash = '';
    try { history.replaceState(null, '', canonical.href); } catch { /* Restricted file/about origins. */ }
    const storageNotice = document.createElement('p');
    storageNotice.id = 'storageNotice';
    storageNotice.className = 'capture-notice';
    storageNotice.setAttribute('role', 'status');
    storageNotice.textContent = 'Armazenamento local indisponível: notas valem só nesta sessão. Exporte antes de recarregar ou trocar a fonte.';
    $('captureNotice').after(storageNotice);
    function showStorageState() {
      storageNotice.hidden = persist;
      document.querySelectorAll('.review-caption').forEach(el => {
        el.textContent = persist ? 'Só neste navegador' : 'Só nesta sessão';
      });
    }
    const previousStore = store;
    store = function(id, patch) { previousStore(id, patch); showStorageState(); };
    showStorageState();
    select.addEventListener('change', () => {
      const hasSessionNotes = !persist && Object.values(checks).some(x => x.note || x.done);
      if (hasSessionNotes && !window.confirm('As notas não foram salvas neste navegador. Exporte a análise antes de sair. Trocar a fonte mesmo assim?')) {
        select.value = isLab() ? 'lab' : 'aurora';
        return;
      }
      const target = new URL(location.href);
      target.searchParams.set('source', select.value);
      target.hash = '';
      location.assign(target.href);
    });
    if(!isLab())return;
    const p=data.provenance;
    document.title='EvidentGraph · Aurora Lab';
    $('contextName').textContent='Aurora Lab';
    document.querySelector('.company').innerHTML='Aurora Lab<small>Execução local capturada</small>';
    document.querySelector('.side-foot .workspace-label').textContent='EVIDÊNCIAS DE LABORATÓRIO';
    document.querySelector('.catalog-totals small').textContent='nesta captura independente';
    document.querySelector('.footer > span').textContent='EvidentGraph · Aurora Lab';
    $('datasetLabel').textContent='Capturado em '+date(p.finished_at);
    $('captureNotice').hidden=false;
    $('captureNotice').textContent=`Captura de execução local · ${date(p.finished_at)} · ${p.spans_used} spans correlacionados de ${p.spans_in_capture} registrados. Dados de negócio fictícios; sem conexão ao vivo.`;
    $('graphScope').querySelector('[value="all"]').textContent='Captura completa';
    $('activityFilter').closest('label').childNodes[0].textContent='Uso antes · v1';
    ACTIVITY.OBSERVED='Uso observado antes · v1';ACTIVITY.UNKNOWN='Uso anterior não confirmado';
    document.querySelector('#aboutDialog .dialog-body').innerHTML=`<p><strong>Aurora Lab</strong> é um ambiente de laboratório separado do cenário sintético Grupo Aurora. Esta interface exibe uma captura histórica, não faz chamadas à API nem roda servidores.</p><p>API FastAPI, clientes HTTP e SQLite executaram localmente. OpenTelemetry registrou a execução. Contratos dos consumidores são declarados. Identificadores e equipes foram normalizados pelo adaptador; processos e criticidade não foram inferidos.</p><p>Arquivo fonte: <code>run.json</code><br>SHA-256: <code>${esc(p.source_sha256)}</code><br>Intervalo: ${esc(p.started_at)} a ${esc(p.finished_at)}.</p><p>O hash identifica os bytes; não autentica a origem de arquivos externos. Respostas são recalculadas pelo Python L1 na preparação, não pelo navegador.</p><ul>${p.limitations.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p>Notas são locais e separadas por captura. Marcar uma verificação não apaga uma falha observada nem envia mensagens. Voltar ao Grupo Aurora carrega outro conjunto sem uni-los.</p>`;
    const originalDetails=openDetails;
    openDetails=function(id,inventory=false){originalDetails(id,inventory);const r=result.consumers.find(r=>r.consumer===id);if(r)$('detailBody').insertAdjacentHTML('afterbegin',phases(r));};
    const baseEvidence=evidenceMarkup;
    evidenceMarkup=function(e){if(e.claim!=='api_contract')return baseEvidence(e);return `<details class="ev"><summary><strong>Contrato OpenAPI capturado · ${esc(e.target_version)}</strong><br><small>${esc(e.id)}</small></summary><pre>${esc(JSON.stringify(e,null,2))}</pre></details>`;};
    report=labReport;
    renderConsumers();inspector();
  });
  document.addEventListener('eg:filtered',decorateRows);
  document.addEventListener('eg:graphinspect',inspector);
})();
