const content = document.querySelector(".report-content");
const status = document.getElementById("report-status");
const controls = document.querySelector(".report-controls");
const select = document.getElementById("page-number");
const previous = document.getElementById("previous-page");
const next = document.getElementById("next-page");
const canvas = document.querySelector(".report-page");
const pageText = document.querySelector(".report-page-text");

let report;
let currentPage = 1;
let rendering = false;

function syncControls() {
  select.disabled = rendering;
  previous.disabled = rendering || currentPage === 1;
  next.disabled = rendering || currentPage === report.numPages;
}

async function showPage(number) {
  if (rendering || number < 1 || number > report.numPages) return;
  rendering = true;
  syncControls();
  content.setAttribute("aria-busy", "true");
  status.textContent = "Carregando página…";
  try {
    const page = await report.getPage(number);
    const original = page.getViewport({ scale: 1 });
    const viewport = page.getViewport({ scale: 1400 / original.width });
    canvas.width = Math.ceil(viewport.width);
    canvas.height = Math.ceil(viewport.height);
    await page.render({ canvas, viewport }).promise;
    const text = await page.getTextContent();
    pageText.textContent = text.items.map(item => item.str ? item.str + (item.hasEOL ? "\n" : " ") : "").join("");
    currentPage = number;
    select.value = number;
    canvas.hidden = false;
    content.scrollTop = 0;
    status.textContent = `Página ${number} de ${report.numPages}`;
  } catch {
    canvas.hidden = true;
    pageText.textContent = "";
    select.value = currentPage;
    status.textContent = "Não foi possível exibir esta página. Use o link “Abrir PDF original”.";
  } finally {
    rendering = false;
    content.setAttribute("aria-busy", "false");
    syncControls();
  }
}

status.textContent = "Carregando relatório…";
try {
  const { getDocument, GlobalWorkerOptions } = await import("./pdfjs/pdf.min.js");
  GlobalWorkerOptions.workerSrc = new URL("./pdfjs/pdf.worker.min.js", import.meta.url).href;
  const url = new URL("../assets/lh-nautical-relatorio-executivo.pdf", import.meta.url).href;
  report = await getDocument({ url, isEvalSupported: false, useWasm: false }).promise;
  for (let number = 1; number <= report.numPages; number++) {
    select.add(new Option(String(number), String(number)));
  }
  previous.addEventListener("click", () => showPage(currentPage - 1));
  next.addEventListener("click", () => showPage(currentPage + 1));
  select.addEventListener("change", () => showPage(Number(select.value)));
  controls.hidden = false;
  await showPage(1);
} catch {
  status.textContent = "Não foi possível carregar o leitor. Use o link “Abrir PDF original”.";
}
