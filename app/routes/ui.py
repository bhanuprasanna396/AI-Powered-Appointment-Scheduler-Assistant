from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])


@router.get("/", response_class=HTMLResponse)
async def home() -> HTMLResponse:
    html = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Appointment Scheduler Assistant</title>
  <style>
    :root {
      --bg: #f3f7f9;
      --card: #ffffff;
      --ink: #102a43;
      --muted: #486581;
      --accent: #0b6e4f;
      --accent-2: #0f766e;
      --tab-off: #e7edf3;
      --border: #d9e2ec;
      --terminal-bg: #0f1720;
      --terminal-ink: #e5f7ff;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: \"Segoe UI\", \"Helvetica Neue\", sans-serif;
      background: radial-gradient(circle at top right, #d6f5e7 0%, var(--bg) 45%);
      color: var(--ink);
      min-height: 100vh;
      padding: 24px;
    }

    .wrap {
      max-width: 980px;
      margin: 0 auto;
      display: grid;
      gap: 16px;
    }

    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px;
      box-shadow: 0 6px 20px rgba(16, 42, 67, 0.08);
    }

    h1 {
      margin: 0 0 10px;
      font-size: 1.6rem;
    }

    p { margin: 0; color: var(--muted); }

    .tabs {
      display: inline-flex;
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
      margin-top: 14px;
    }

    .tab-btn {
      border: 0;
      padding: 10px 14px;
      cursor: pointer;
      font-weight: 700;
      color: var(--ink);
      background: var(--tab-off);
    }

    .tab-btn.active {
      color: #fff;
      background: linear-gradient(120deg, var(--accent), var(--accent-2));
    }

    .panel {
      display: none;
      margin-top: 12px;
    }

    .panel.active {
      display: block;
    }

    label {
      display: block;
      font-weight: 600;
      margin: 0 0 6px;
    }

    textarea, input[type=file] {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px;
      font-size: 0.98rem;
      background: #fff;
    }

    textarea {
      min-height: 110px;
      resize: vertical;
    }

    .hint {
      color: var(--muted);
      font-size: 0.9rem;
      margin-top: 8px;
    }

    .row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
      align-items: center;
    }

    .action-btn {
      border: 0;
      border-radius: 10px;
      padding: 10px 14px;
      font-weight: 600;
      cursor: pointer;
      color: #fff;
      background: linear-gradient(120deg, var(--accent), var(--accent-2));
    }

    .ghost {
      background: #eaf2f7;
      color: var(--ink);
    }

    pre {
      margin: 0;
      border-radius: 12px;
      border: 1px solid #203244;
      padding: 14px;
      background: var(--terminal-bg);
      color: var(--terminal-ink);
      overflow: auto;
      min-height: 260px;
      font-size: 0.9rem;
    }
  </style>
</head>
<body>
  <main class=\"wrap\">
    <section class=\"card\">
      <h1>AI Appointment Scheduler Assistant</h1>
      <p>Choose one mode, submit text or image, and view structured JSON output.</p>

      <div class=\"tabs\" role=\"tablist\" aria-label=\"Input mode\">
        <button id=\"textTab\" class=\"tab-btn active\" type=\"button\" role=\"tab\" aria-selected=\"true\">Text</button>
        <button id=\"imageTab\" class=\"tab-btn\" type=\"button\" role=\"tab\" aria-selected=\"false\">Image</button>
      </div>

      <div id=\"textPanel\" class=\"panel active\" role=\"tabpanel\">
        <label for=\"textInput\">Text Input</label>
        <textarea id=\"textInput\" placeholder=\"Type appointment request here...\"></textarea>
      </div>

      <div id=\"imagePanel\" class=\"panel\" role=\"tabpanel\">
        <label for=\"imageInput\">Image Input</label>
        <input id=\"imageInput\" type=\"file\" accept=\"image/*\" />
      </div>

      <p class=\"hint\">Only one input type is used at a time. Output is formatted step-by-step for the assignment.</p>

      <div class=\"row\">
        <button id=\"runBtn\" class=\"action-btn\" type=\"button\">Run Pipeline (/process)</button>
        <button id=\"ocrBtn\" class=\"action-btn ghost\" type=\"button\">OCR Only (/ocr)</button>
      </div>
    </section>

    <section class=\"card\">
      <label>Output</label>
      <pre id=\"output\">Waiting for input...</pre>
    </section>
  </main>

  <script>
    let activeMode = 'text';

    function switchMode(mode) {
      activeMode = mode;
      const textTab = document.getElementById('textTab');
      const imageTab = document.getElementById('imageTab');
      const textPanel = document.getElementById('textPanel');
      const imagePanel = document.getElementById('imagePanel');
      const textInput = document.getElementById('textInput');
      const imageInput = document.getElementById('imageInput');
      const output = document.getElementById('output');

      if (mode === 'text') {
        textTab.classList.add('active');
        textTab.setAttribute('aria-selected', 'true');
        imageTab.classList.remove('active');
        imageTab.setAttribute('aria-selected', 'false');

        textPanel.classList.add('active');
        imagePanel.classList.remove('active');
        imageInput.value = '';
      } else {
        imageTab.classList.add('active');
        imageTab.setAttribute('aria-selected', 'true');
        textTab.classList.remove('active');
        textTab.setAttribute('aria-selected', 'false');

        imagePanel.classList.add('active');
        textPanel.classList.remove('active');
        textInput.value = '';
      }

      output.textContent = 'Waiting for input...';
    }

    async function fileToBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result).split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    }

    async function buildPayload() {
      const payload = {};
      const textValue = document.getElementById('textInput').value.trim();
      const imageFile = document.getElementById('imageInput').files[0];

      if (activeMode === 'text') {
        if (textValue) payload.text = textValue;
      } else {
        if (imageFile) payload.image = await fileToBase64(imageFile);
      }

      return payload;
    }

    function prettyJson(value) {
      return JSON.stringify(value, null, 2);
    }

    function formatProcessOutput(data) {
      const ocrStep = data.ocr || {};
      const extractionStep = data.extraction || {};
      const normalizationStep = data.normalization || {};
      const finalStep = data.final || {};

      const guardrail = finalStep.status === 'needs_clarification'
        ? { status: finalStep.status, message: finalStep.message }
        : { status: finalStep.status };

      const finalAppointment = finalStep.appointment
        ? { appointment: finalStep.appointment, status: finalStep.status }
        : guardrail;

      return [
        'Step 1 - OCR/Text Extraction',
        prettyJson(ocrStep),
        '',
        'Step 2 - Entity Extraction',
        prettyJson(extractionStep),
        '',
        'Step 3 - Normalization (Asia/Kolkata)',
        prettyJson(normalizationStep),
        '',
        'Guardrail / Exit Condition',
        prettyJson(guardrail),
        '',
        'Step 4 - Final Appointment JSON',
        prettyJson(finalAppointment),
      ].join('\\n');
    }

    async function callApi(path) {
      const out = document.getElementById('output');
      out.textContent = 'Processing...';

      try {
        const payload = await buildPayload();

        if (!payload.text && !payload.image) {
          out.textContent = activeMode === 'text'
            ? 'Please enter text before submitting.'
            : 'Please choose an image before submitting.';
          return;
        }

        const res = await fetch(path, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const bodyText = await res.text();
        if (!bodyText || !bodyText.trim()) {
          out.textContent = `No response body received (HTTP ${res.status}).`;
          return;
        }

        let data;
        try {
          data = JSON.parse(bodyText);
        } catch {
          out.textContent = `Non-JSON response (HTTP ${res.status}):\n${bodyText}`;
          return;
        }

        if (path === '/process' && !data.detail) {
          out.textContent = formatProcessOutput(data);
          return;
        }

        out.textContent = prettyJson(data);
      } catch (err) {
        out.textContent = `Request failed: ${err}`;
      }
    }

    document.getElementById('textTab').addEventListener('click', () => switchMode('text'));
    document.getElementById('imageTab').addEventListener('click', () => switchMode('image'));
    document.getElementById('runBtn').addEventListener('click', () => callApi('/process'));
    document.getElementById('ocrBtn').addEventListener('click', () => callApi('/ocr'));
  </script>
</body>
</html>
"""

    return HTMLResponse(
        content=html,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
