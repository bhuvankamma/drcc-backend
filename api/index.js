// api/index.js
const express = require('express');
const fs = require('fs');
const path = require('path');
const { URLSearchParams } = require('url');
const { Transform, Readable } = require('stream');

const app = express();

// ----------------------------------------------------------------------
// Allowed origins - keep this list in sync with your frontend domains
// ----------------------------------------------------------------------
const allowedOrigins = [
  "https://www.yuvasaathi.in",
  "https://hi.yuvasaathi.in",
  "http://localhost:3000",
  /\.vercel\.app$/ // allow all vercel subdomains (regex)
];

// ----------------------------------------------------------------------
// CORS middleware
// ----------------------------------------------------------------------
app.use((req, res, next) => {
  const origin = req.headers.origin;

  if (origin) {
    const matched = allowedOrigins.some(item => {
      if (item instanceof RegExp) return item.test(origin);
      return item === origin;
    });

    if (matched) {
      res.setHeader('Access-Control-Allow-Origin', origin);
      res.setHeader('Vary', 'Origin');
    } else {
      console.warn(`[CORS] Blocked origin: ${origin}`);
    }
  }

  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');

  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }

  next();
});

// ----------------------------------------------------------------------
// Body parser
// ----------------------------------------------------------------------
app.use(express.json({ limit: '1mb' }));

// ----------------------------------------------------------------------
// REMOVE TRANSLATION ENDPOINT ↓↓↓
// (nothing related to /api/translate exists anymore)
// ----------------------------------------------------------------------

// ----------------------------------------------------------------------
// Ollama Stream Parsing
// ----------------------------------------------------------------------
class OllamaStreamParser extends Transform {
  constructor(options) {
    super(options);
    this._buffer = '';
  }

  _transform(chunk, encoding, callback) {
    try {
      this._buffer += chunk.toString();
      let lastNewline = this._buffer.lastIndexOf('\n');

      if (lastNewline !== -1) {
        const chunkToProcess = this._buffer.substring(0, lastNewline);
        this._buffer = this._buffer.substring(lastNewline + 1);

        chunkToProcess.split('\n').forEach(line => {
          if (!line) return;
          try {
            const parsed = JSON.parse(line);
            if (typeof parsed.response === 'string') {
              this.push(parsed.response);
            } else if (parsed.token) {
              this.push(String(parsed.token));
            } else if (parsed.text) {
              this.push(String(parsed.text));
            }
          } catch (e) {
            this.push(line);
          }
        });
      }
    } catch (err) {}

    callback();
  }

  _flush(callback) {
    if (this._buffer && this._buffer.trim()) {
      try {
        const parsed = JSON.parse(this._buffer.trim());
        if (typeof parsed.response === 'string') this.push(parsed.response);
        else if (parsed.token) this.push(String(parsed.token));
        else if (parsed.text) this.push(String(parsed.text));
      } catch (e) {
        this.push(this._buffer);
      }
    }
    callback();
  }
}

// ----------------------------------------------------------------------
// MAP DATA
// ----------------------------------------------------------------------
function loadMapData(fileName) {
  const candidatePaths = [
    path.join(__dirname, '..', 'data', fileName),
    path.join(path.dirname(__dirname), 'data', fileName),
    path.join('/tmp', 'data', fileName),
    path.join(__dirname, 'data', fileName)
  ];

  for (const p of candidatePaths) {
    if (fs.existsSync(p)) {
      console.log(`[MAP] using file: ${p}`);
      return JSON.parse(fs.readFileSync(p, 'utf8'));
    }
  }

  throw new Error(`Map file not found: ${fileName}`);
}

app.get('/api/bihar-map-data', (req, res) => {
  try {
    const data = loadMapData('bihar_districts.geojson');
    return res.json(data);
  } catch (err) {
    console.error('[MAP] error', err);
    return res.status(500).json({ error: err.message });
  }
});

app.get('/api/district-data/:district_name', (req, res) => {
  try {
    const blocksData = loadMapData('bihar_blocks.geojson');
    const districtName = (req.params.district_name || '').toLowerCase();
    const features = (blocksData.features || []).filter(f =>
      (f.properties && f.properties.district_name || '').toLowerCase() === districtName
    );

    if (!features.length) return res.status(404).json({ error: 'No blocks found' });
    return res.json({ map_geojson: { ...blocksData, features } });
  } catch (err) {
    console.error('[MAP] district-data error', err);
    return res.status(500).json({ error: err.message });
  }
});

app.get('/api/mandal-data/:mandal_name', (req, res) => {
  try {
    const villagesData = loadMapData('bihar_villages.geojson');
    const mandalName = (req.params.mandal_name || '').toLowerCase();
    const features = (villagesData.features || []).filter(f =>
      (f.properties && f.properties.mandal_name || '').toLowerCase() === mandalName
    );

    if (!features.length) return res.status(404).json({ error: 'No villages found' });
    return res.json({ map_geojson: { ...villagesData, features } });
  } catch (err) {
    console.error('[MAP] mandal-data error', err);
    return res.status(500).json({ error: err.message });
  }
});

// ----------------------------------------------------------------------
// JOBS
// ----------------------------------------------------------------------
app.get('/api/jobs', async (req, res) => {
  const ADZUNA_APP_ID = process.env.ADZUNA_APP_ID;
  const ADZUNA_APP_KEY = process.env.ADZUNA_APP_KEY;
  const ADZUNA_BASE_URL = 'https://api.adzuna.com/v1/api/jobs';

  if (!ADZUNA_APP_ID || !ADZUNA_APP_KEY) {
    return res.status(500).json({ error: 'Adzuna API keys missing' });
  }

  const { q = 'IT jobs', location = 'India', page = 1, rpp = 50 } = req.query;

  const endpoint = `${ADZUNA_BASE_URL}/in/search/${page}`;
  const params = new URLSearchParams({
    app_id: ADZUNA_APP_ID,
    app_key: ADZUNA_APP_KEY,
    what: q,
    where: location,
    results_per_page: rpp
  });

  try {
    const apiResp = await fetch(`${endpoint}?${params.toString()}`);
    if (!apiResp.ok) {
      const txt = await apiResp.text().catch(() => '');
      console.error('[JOBS] Adzuna error', apiResp.status, txt);
      return res.status(502).json({ error: 'Adzuna error', status: apiResp.status, body: txt });
    }
    const data = await apiResp.json();
    return res.json(data);
  } catch (err) {
    console.error('[JOBS] request failed', err);
    return res.status(503).json({ error: 'External job API failed', details: String(err) });
  }
});

app.get('/api/jobs/recommendations', async (req, res) => {
  const { q, location = 'India', rpp = 10 } = req.query;
  if (!q) return res.status(400).json({ error: 'Missing q parameter' });

  const ADZUNA_APP_ID = process.env.ADZUNA_APP_ID;
  const ADZUNA_APP_KEY = process.env.ADZUNA_APP_KEY;
  const BASE_URL = 'https://api.adzuna.com/v1/api/jobs/in/search/1';

  const params = new URLSearchParams({
    app_id: ADZUNA_APP_ID,
    app_key: ADZUNA_APP_KEY,
    what: q,
    where: location,
    results_per_page: rpp
  });

  try {
    const apiResp = await fetch(`${BASE_URL}?${params.toString()}`);
    if (!apiResp.ok) {
      const txt = await apiResp.text().catch(() => '');
      console.error('[JOBS.REC] Adzuna error', apiResp.status, txt);
      return res.status(502).json({ error: 'Adzuna error', status: apiResp.status, body: txt });
    }
    const data = await apiResp.json();
    return res.json({ job_results: data.results || [] });
  } catch (err) {
    console.error('[JOBS.REC] request failed', err);
    return res.status(503).json({ error: 'Recommendation API failed', details: String(err) });
  }
});

// ----------------------------------------------------------------------
// CHATBOT
// ----------------------------------------------------------------------
async function handleChatRequest(req, res) {
  const OLLAMA_BASE_URL = process.env.OLLAMA_API_URL;
  const { model = 'tinyllama', prompt, message, system = 'You are the helpful Bihar Job AI Chat assistant.' } = req.body || {};

  const userMessage = prompt || message || '';

  if (!OLLAMA_BASE_URL) {
    return res.status(503).json({ error: 'OLLAMA_API_URL missing' });
  }
  if (!userMessage) {
    return res.status(400).json({ error: 'No message provided' });
  }

  const composedPrompt = `${system}\n\nUser: ${userMessage}\nAssistant:`;

  let base = OLLAMA_BASE_URL;
  if (!base.startsWith('http')) base = 'http://' + base;
  const OLLAMA_URL = `${base.replace(/\/$/, '')}/api/generate`;

  try {
    const apiResponse = await fetch(OLLAMA_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        prompt: composedPrompt,
        system,
        stream: true
      }),
    });

    if (!apiResponse.ok) {
      const txt = await apiResponse.text().catch(() => '');
      console.error('[CHAT] Ollama error', apiResponse.status, txt);
      return res.status(502).json({ error: 'Ollama returned an error', status: apiResponse.status, body: txt });
    }

    if (apiResponse.body && typeof apiResponse.body.getReader === 'function') {
      res.setHeader('Content-Type', 'text/plain; charset=utf-8');
      res.setHeader('Connection', 'keep-alive');

      const nodeReadable = Readable.fromWeb(apiResponse.body);
      const parser = new OllamaStreamParser();

      nodeReadable.pipe(parser).pipe(res);

      parser.on('end', () => res.end());
      parser.on('error', () => {
        try { res.end(); } catch (e) {}
      });

      return;
    }

    const textBody = await apiResponse.text().catch(() => '');
    try {
      const json = JSON.parse(textBody);
      if (json && (json.response || json.output || json.result)) {
        const reply = json.response ||
          (Array.isArray(json.output) ? json.output[0]?.text : null) ||
          json.result || JSON.stringify(json);

        return res.json({ reply });
      }
    } catch (e) {
      return res.json({ reply: textBody });
    }

    return res.json({ reply: textBody });
  } catch (err) {
    console.error('[CHAT] Exception', err);
    return res.status(503).json({ error: 'Chat backend failed', details: String(err) });
  }
}

app.options('/api/chat', (req, res) => res.sendStatus(200));
app.options('/api/chatbot', (req, res) => res.sendStatus(200));

app.post('/api/chat', handleChatRequest);
app.post('/api/chatbot', handleChatRequest);

// ----------------------------------------------------------------------
// Health
// ----------------------------------------------------------------------
app.get('/', (req, res) => res.send('API is running.'));
app.get('/api', (req, res) => res.json({ status: 'ok' }));

app.options(/.*/, (req, res) => res.sendStatus(200));

// not found
app.use((req, res) => {
  if (!['GET', 'POST'].includes(req.method)) {
    return res.status(405).json({ error: `Method ${req.method} Not Allowed` });
  }
  return res.status(404).json({ error: `Endpoint not found: ${req.path}` });
});

module.exports = app;
