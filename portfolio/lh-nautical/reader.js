const status = document.getElementById("report-status");
const pages = document.querySelector(".report-pages");
const originalPdf = new URL("../assets/lh-nautical-relatorio-executivo.pdf", import.meta.url);

function createSheet(page, total) {
  const size = page.getViewport({ scale: 1 });
  const sheet = document.createElement("figure");
  sheet.className = "report-sheet";
  sheet.dataset.page = page.pageNumber;
  sheet.style.aspectRatio = `${size.width} / ${size.height}`;
  sheet.setAttribute("aria-label", `Página ${page.pageNumber} de ${total}`);
  return sheet;
}

async function renderSheet(sheet, page) {
  sheet.setAttribute("aria-busy", "true");
  try {
    const canvas = document.createElement("canvas");
    canvas.className = "report-page";
    canvas.setAttribute("aria-hidden", "true");

    const original = page.getViewport({ scale: 1 });
    const pixels = Math.min(1400, sheet.clientWidth * Math.min(window.devicePixelRatio || 1, 2));
    const viewport = page.getViewport({ scale: pixels / original.width });
    canvas.width = Math.ceil(viewport.width);
    canvas.height = Math.ceil(viewport.height);

    const [, text] = await Promise.all([page.render({ canvas, viewport }).promise, page.getTextContent()]);
    const accessibleText = document.createElement("div");
    accessibleText.className = "report-page-text";
    accessibleText.textContent = text.items.map(item => item.str ? item.str + (item.hasEOL ? "\n" : " ") : "").join("");
    sheet.append(canvas, accessibleText);
  } catch {
    const message = document.createElement("p");
    const link = document.createElement("a");
    message.className = "report-error";
    message.textContent = "Não foi possível exibir esta página. ";
    link.href = originalPdf.href;
    link.textContent = "Abrir PDF original";
    message.append(link);
    sheet.append(message);
  } finally {
    sheet.removeAttribute("aria-busy");
  }
}

status.textContent = "Carregando relatório…";
try {
  const { getDocument, GlobalWorkerOptions } = await import("./pdfjs/pdf.min.js");
  GlobalWorkerOptions.workerSrc = new URL("./pdfjs/pdf.worker.min.js", import.meta.url).href;
  const report = await getDocument({ url: originalPdf.href, isEvalSupported: false, useWasm: false }).promise;
  const documentPages = await Promise.all(
    Array.from({ length: report.numPages }, (_, index) => report.getPage(index + 1))
  );
  const sheets = documentPages.map(page => createSheet(page, report.numPages));
  pages.append(...sheets);
  status.textContent = `${report.numPages} páginas`;

  const observer = new IntersectionObserver(entries => {
    for (const { target, isIntersecting } of entries) {
      if (!isIntersecting) continue;
      observer.unobserve(target);
      void renderSheet(target, documentPages[Number(target.dataset.page) - 1]);
    }
  }, { rootMargin: "420px 0px" });
  for (const sheet of sheets) observer.observe(sheet);
} catch {
  status.textContent = "Não foi possível carregar o leitor. Use o link “Abrir PDF original”.";
}
