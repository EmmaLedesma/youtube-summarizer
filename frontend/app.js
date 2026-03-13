/* ═══════════════════════════════════════════════════════════
   YT Summarizer — Emmanuel Ledesma
   app.js
   ═══════════════════════════════════════════════════════════ */

const API_URL      = 'https://8fbiu33ok7.execute-api.us-east-1.amazonaws.com/dev/summarize';
const SUPADATA_URL = 'https://api.supadata.ai/v1/youtube/transcript';
const SUPADATA_KEY = 'sd_27f668e05bce4d8026fb537538ab7050';

const LANG_NAMES = {
  auto: 'Auto', es: 'Spanish', en: 'English', pt: 'Portuguese',
  fr: 'French', de: 'German', it: 'Italian',
  ja: 'Japanese', ko: 'Korean', zh: 'Chinese',
};

const sessionHistory = [];

const urlInput       = document.getElementById('urlInput');
const langSelect     = document.getElementById('langSelect');
const btnSummarize   = document.getElementById('btnSummarize');
const statusBar      = document.getElementById('statusBar');
const statusText     = document.getElementById('statusText');
const statusIcon     = document.getElementById('statusIcon');
const progressSteps  = document.getElementById('progressSteps');
const videoPanel     = document.getElementById('videoPanel');
const summaryPanel   = document.getElementById('summaryPanel');
const videoIframe    = document.getElementById('videoIframe');
const cachedBadge    = document.getElementById('cachedBadge');
const execSummary    = document.getElementById('execSummary');
const keyPointsList  = document.getElementById('keyPoints');
const topicsRow      = document.getElementById('topicsRow');
const metaRow        = document.getElementById('metaRow');
const historyGrid    = document.getElementById('historyGrid');

// ── UTILITIES ───────────────────────────────────────────────

function extractVideoId(url) {
  const patterns = [
    /(?:v=)([a-zA-Z0-9_-]{11})/,
    /(?:youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    /(?:embed\/)([a-zA-Z0-9_-]{11})/,
  ];
  for (const p of patterns) {
    const m = url.match(p);
    if (m) return m[1];
  }
  return null;
}

function setStatus(type, text, iconPath) {
  statusBar.className = `status-bar show ${type}`;
  statusText.textContent = text;
  statusIcon.innerHTML = iconPath;
}

function setStep(n) {
  ['step1','step2','step3','step4'].forEach((id, i) => {
    const el = document.getElementById(id);
    if (i + 1 < n)        el.className = 'step done';
    else if (i + 1 === n) el.className = 'step active';
    else                   el.className = 'step';
  });
}

// ── TRANSCRIPT via Supadata ──────────────────────────────────

async function fetchTranscript(videoId, langCode) {
  let url = `${SUPADATA_URL}?videoId=${videoId}&text=true`;
  if (langCode && langCode !== 'auto') url += `&lang=${langCode}`;

  const res = await fetch(url, { headers: { 'x-api-key': SUPADATA_KEY } });

  if (!res.ok) {
    if (res.status === 404) throw new Error('Este video no tiene subtítulos disponibles.');
    if (res.status === 429) throw new Error('Límite de requests alcanzado. Intentá en unos minutos.');
    throw new Error(`Error obteniendo subtítulos (${res.status})`);
  }

  const data = await res.json();
  const text = (data.content || '').trim();
  const lang = data.lang || langCode || 'en';
  if (!text) throw new Error('El transcript está vacío.');
  return { text, language: lang };
}

// ── RENDER ──────────────────────────────────────────────────

function renderSummary(data, videoId) {
  const s = data.summary;

  execSummary.textContent = s.executiveSummary || '';
  keyPointsList.innerHTML = (s.keyPoints || []).map(p => `<li>${p}</li>`).join('');
  topicsRow.innerHTML = (s.mainTopics || []).map(t => `<span class="topic-chip">${t}</span>`).join('');

  metaRow.innerHTML = `
    <span class="meta-chip">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="2" y1="12" x2="22" y2="12"/>
        <path d="M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20"/>
      </svg>
      ${s.detectedLanguage || '—'}
    </span>
    <span class="meta-chip">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="2" y="3" width="20" height="14" rx="2"/>
        <line x1="8" y1="21" x2="16" y2="21"/>
        <line x1="12" y1="17" x2="12" y2="21"/>
      </svg>
      ${s.contentType || '—'}
    </span>
    <span class="meta-chip">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <polyline points="12 6 12 12 16 14"/>
      </svg>
      ${new Date(data.createdAt).toLocaleString('es-AR')}
    </span>
  `;

  cachedBadge.style.display = data.cached ? 'inline-flex' : 'none';
  videoIframe.src = `https://www.youtube.com/embed/${videoId}`;
  videoPanel.classList.add('show');
  summaryPanel.classList.add('show');
}

// ── HISTORY ─────────────────────────────────────────────────

function addToHistory(videoId, summary) {
  if (!sessionHistory.find(i => i.videoId === videoId)) {
    sessionHistory.unshift({ videoId, summary, ts: new Date() });
  }
  renderHistory();
}

function renderHistory() {
  if (!sessionHistory.length) {
    historyGrid.innerHTML = '<div class="history-empty">Todavía no resumiste ningún video en esta sesión.</div>';
    return;
  }
  historyGrid.innerHTML = sessionHistory.map(item => `
    <div class="history-card" onclick="loadFromHistory('${item.videoId}')">
      <div class="hc-id">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="23 7 16 12 23 17 23 7"/>
          <rect x="1" y="5" width="15" height="14" rx="2"/>
        </svg>
        ${item.videoId}
      </div>
      <div class="hc-summary">${item.summary.executiveSummary || ''}</div>
      <div class="hc-date">${item.ts.toLocaleString('es-AR')}</div>
    </div>
  `).join('');
}

function loadFromHistory(videoId) {
  const item = sessionHistory.find(i => i.videoId === videoId);
  if (!item) return;
  videoIframe.src = `https://www.youtube.com/embed/${videoId}`;
  cachedBadge.style.display = 'inline-flex';
  execSummary.textContent = item.summary.executiveSummary || '';
  keyPointsList.innerHTML = (item.summary.keyPoints || []).map(p => `<li>${p}</li>`).join('');
  topicsRow.innerHTML = (item.summary.mainTopics || []).map(t => `<span class="topic-chip">${t}</span>`).join('');
  metaRow.innerHTML = '';
  videoPanel.classList.add('show');
  summaryPanel.classList.add('show');
  document.getElementById('summarizer').scrollIntoView({ behavior: 'smooth' });
}

// ── MAIN FLOW ────────────────────────────────────────────────

async function handleSummarize() {
  const url = urlInput.value.trim();
  const langCode = langSelect.value;

  if (!url) {
    setStatus('error', 'Ingresá una URL de YouTube.',
      '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>');
    return;
  }

  const videoId = extractVideoId(url);
  if (!videoId) {
    setStatus('error', 'URL inválida. Usá el formato youtube.com/watch?v=... o youtu.be/...',
      '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>');
    return;
  }

  btnSummarize.disabled = true;
  videoPanel.classList.remove('show');
  summaryPanel.classList.remove('show');
  progressSteps.classList.add('show');

  try {
    setStep(1);
    setStatus('info', 'Cargando video…', '<circle cx="12" cy="12" r="10"/>');
    videoIframe.src = `https://www.youtube.com/embed/${videoId}`;
    cachedBadge.style.display = 'none';
    videoPanel.classList.add('show');

    setStep(2);
    setStatus('info', 'Obteniendo subtítulos…',
      '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>');
    const { text: transcriptText, language } = await fetchTranscript(videoId, langCode);

    setStep(3);
    setStatus('info', 'Claude AI está analizando el contenido…',
      '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>');

    // Determinar idioma para el resumen
    const summaryLang = langCode !== 'auto'
      ? (LANG_NAMES[langCode] || langCode)
      : language;

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ videoId, transcriptText, language: summaryLang }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.message || `Error del servidor (${response.status})`);
    }

    const data = await response.json();

    setStep(4);
    renderSummary(data, videoId);
    addToHistory(videoId, data.summary);

    setStatus(
      'success',
      data.cached ? '¡Resumen cargado desde caché!' : '¡Resumen generado con éxito!',
      '<path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>'
    );
    setTimeout(() => progressSteps.classList.remove('show'), 2000);

  } catch (err) {
    setStatus('error', err.message,
      '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>');
    progressSteps.classList.remove('show');
  } finally {
    btnSummarize.disabled = false;
  }
}

btnSummarize.addEventListener('click', handleSummarize);
urlInput.addEventListener('keydown', e => { if (e.key === 'Enter') handleSummarize(); });
document.querySelectorAll('.nav-pill').forEach(pill => {
  pill.addEventListener('click', function () {
    document.querySelectorAll('.nav-pill').forEach(p => p.classList.remove('active'));
    this.classList.add('active');
  });
});