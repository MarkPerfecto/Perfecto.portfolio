const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const dotenv = require('dotenv');
const express = require('express');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const multer = require('multer');
const sanitizeHtml = require('sanitize-html');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.disable('x-powered-by');
app.use(helmet({
  contentSecurityPolicy: false,
}));

app.use(rateLimit({
  windowMs: 60 * 1000,
  limit: 120,
  standardHeaders: 'draft-7',
  legacyHeaders: false,
}));

app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

const PUBLIC_DIR = path.join(__dirname, 'public');
const UPLOADS_DIR = path.join(__dirname, 'uploads');

app.use(express.static(PUBLIC_DIR));
app.use('/uploads', express.static(UPLOADS_DIR));

function safeSendFile(res, filePath) {
  res.sendFile(filePath, (err) => {
    if (err) {
      res.status(err.statusCode || 500).send('Not found');
    }
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function buildBookIndexHtml({ title, pages }) {
  const safeTitle = escapeHtml(title);
  const items = pages
    .map((p) => {
      const url = escapeHtml(p.url);
      const label = `Page ${p.page}`;
      return `{ page: ${Number(p.page)}, url: "${url}", label: "${label}" }`;
    })
    .join(',\n');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${safeTitle}</title>
  <style>
    :root{--bg:#f9fafb;--card:#fff;--text:#111827;--muted:#6b7280;--border:#e5e7eb;--accent:#2563eb;}
    *{box-sizing:border-box}
    body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text);line-height:1.55}
    a{color:inherit;text-decoration:none}
    .wrap{max-width:980px;margin:0 auto;padding:28px}
    .top{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
    h1{margin:0;font-size:26px}
    .meta{color:var(--muted);margin-top:6px}
    .card{background:var(--card);border:1px solid var(--border);border-radius:16px;box-shadow:0 10px 25px rgba(0,0,0,.06);padding:18px;margin-top:16px}
    .row{display:flex;gap:12px;flex-wrap:wrap;align-items:center;justify-content:space-between}
    .search{flex:1;min-width:240px;display:flex;gap:10px;align-items:center}
    input{width:100%;padding:12px 14px;border:1px solid var(--border);border-radius:12px;outline:none}
    input:focus{border-color:rgba(37,99,235,.7);box-shadow:0 0 0 4px rgba(37,99,235,.12)}
    .btn{padding:10px 14px;border-radius:999px;border:1px solid var(--border);background:#fff;cursor:pointer;font-weight:600}
    .btn.primary{border-color:rgba(37,99,235,.35);color:var(--accent)}
    .grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:14px}
    @media (min-width: 780px){.grid{grid-template-columns:repeat(4,minmax(0,1fr));}}
    .item{padding:12px 12px;border:1px solid var(--border);border-radius:14px;background:#fff;transition:transform .15s ease, box-shadow .15s ease}
    .item:hover{transform:translateY(-2px);box-shadow:0 10px 20px rgba(0,0,0,.08)}
    .item a{display:block;color:var(--accent);font-weight:700}
    .pager{display:flex;gap:10px;align-items:center;justify-content:flex-end;margin-top:14px;color:var(--muted)}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div>
        <h1>${safeTitle}</h1>
        <div class="meta">Browse pages. Search supports page number (e.g., 12).</div>
      </div>
      <a class="btn primary" href="/books">Back to Books</a>
    </div>

    <div class="card">
      <div class="row">
        <div class="search">
          <input id="q" placeholder="Search pages…" autocomplete="off" />
        </div>
        <div class="row" style="justify-content:flex-end">
          <button class="btn" id="prev">Prev</button>
          <button class="btn" id="next">Next</button>
        </div>
      </div>
      <div id="grid" class="grid"></div>
      <div class="pager"><span id="status"></span></div>
    </div>
  </div>

  <script>
    const PAGES = [${items}];
    const pageSize = 16;
    let page = 1;
    let query = '';

    const qEl = document.getElementById('q');
    const grid = document.getElementById('grid');
    const status = document.getElementById('status');
    const prev = document.getElementById('prev');
    const next = document.getElementById('next');

    function filtered() {
      if (!query) return PAGES;
      const q = query.trim().toLowerCase();
      return PAGES.filter(p => String(p.page).includes(q) || p.label.toLowerCase().includes(q));
    }

    function render() {
      const all = filtered();
      const pageCount = Math.max(1, Math.ceil(all.length / pageSize));
      page = Math.min(page, pageCount);
      const start = (page - 1) * pageSize;
      const slice = all.slice(start, start + pageSize);

      grid.innerHTML = '';
      slice.forEach(p => {
        const el = document.createElement('div');
        el.className = 'item';
        el.innerHTML = '<a href="' + p.url + '" target="_blank" rel="noreferrer">' + p.label + '</a>';
        grid.appendChild(el);
      });

      prev.disabled = page <= 1;
      next.disabled = page >= pageCount;
      status.textContent = 'Showing ' + slice.length + ' of ' + all.length + ' • Page ' + page + ' / ' + pageCount;
    }

    qEl.addEventListener('input', (e) => {
      query = e.target.value;
      page = 1;
      render();
    });

    prev.addEventListener('click', () => { page = Math.max(1, page - 1); render(); });
    next.addEventListener('click', () => { page = page + 1; render(); });
    render();
  </script>
</body>
</html>`;
}

// Page routes
app.get(['/', '/home'], (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'index.html')));
app.get('/gallery', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'gallery.html')));
app.get('/projects', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'projects.html')));
app.get('/projects/character-creator', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'projects', 'character_creator.html')));
app.get('/projects/hotel-reservation', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'projects', 'hotel_reservation.html')));
app.get('/projects/notes-certifications', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'projects', 'notes_certifications.html')));
app.get('/projects/anigen', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'projects', 'anigen.html')));
app.get('/projects/quiz_builder', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'projects', 'quiz_builder.html')));
app.get('/projects/kanban_board', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'projects', 'kanban_board.html')));
app.get('/projects/threat_decoder', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'projects', 'threat_decoder.html')));
app.get('/projects/ai_notes', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'projects', 'ai_notes.html')));
app.get('/projects/timeline', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'projects', 'timeline.html')));
app.get('/blog', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'blog.html')));
app.get('/books', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'books.html')));
app.get('/videos', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'videos.html')));
app.get('/files', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'files.html')));
app.get('/contact', (req, res) => safeSendFile(res, path.join(PUBLIC_DIR, 'contact.html')));

// Simple blog API (JSON backed)
const postsStore = require('./store/posts');
const booksStore = require('./store/books');

function makeIdFromName(name) {
  const base = String(name || '')
    .toLowerCase()
    .replace(/\.[^/.]+$/, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
    .slice(0, 60);

  return `${base || 'book'}-${Date.now()}`;
}

function runPdfParser({ pdfAbsPath, outAbsDir, title }) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, 'scripts', 'pdf_parser.py');
    const py = spawn('python', [
      scriptPath,
      '--pdf', pdfAbsPath,
      '--out', outAbsDir,
      '--title', title,
    ]);

    let stdout = '';
    let stderr = '';

    py.stdout.on('data', (d) => (stdout += d.toString()));
    py.stderr.on('data', (d) => (stderr += d.toString()));

    py.on('error', (err) => {
      reject(err);
    });

    py.on('close', (code) => {
      if (code !== 0) {
        const err = new Error(`pdf_parser.py exited with code ${code}`);
        err.details = stderr || stdout;
        reject(err);
        return;
      }

      try {
        const parsed = JSON.parse(stdout.trim() || '{}');
        resolve(parsed);
      } catch (e) {
        const err = new Error('Failed to parse pdf_parser.py output as JSON');
        err.details = stdout;
        reject(err);
      }
    });
  });
}

app.get('/api/books', async (req, res) => {
  const books = await booksStore.listBooks();
  res.json({ books });
});

app.get('/api/blog', async (req, res) => {
  const posts = await postsStore.listPosts();
  res.json({ posts });
});

app.post('/api/blog', async (req, res) => {
  const title = typeof req.body?.title === 'string' ? req.body.title.trim() : '';
  const body = typeof req.body?.body === 'string' ? req.body.body : '';

  if (!title || !body) {
    return res.status(400).json({ error: 'title and body are required' });
  }

  const cleanTitle = sanitizeHtml(title, { allowedTags: [], allowedAttributes: {} });
  const cleanBody = sanitizeHtml(body, {
    allowedTags: ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li', 'code', 'pre', 'a'],
    allowedAttributes: { a: ['href', 'rel', 'target'] },
    allowedSchemes: ['http', 'https', 'mailto']
  });

  const created = await postsStore.addPost({ title: cleanTitle, body: cleanBody });
  res.status(201).json({ post: created });
});

// Uploads
function makeStorage(subdir) {
  return multer.diskStorage({
    destination: (req, file, cb) => cb(null, path.join(UPLOADS_DIR, subdir)),
    filename: (req, file, cb) => {
      const safeBase = path.basename(file.originalname).replace(/[^a-zA-Z0-9._-]/g, '_');
      cb(null, `${Date.now()}_${safeBase}`);
    }
  });
}

const uploadPdf = multer({ storage: makeStorage('pdfs'), limits: { fileSize: 25 * 1024 * 1024 } });
const uploadVideo = multer({ storage: makeStorage('videos'), limits: { fileSize: 200 * 1024 * 1024 } });
const uploadFile = multer({ storage: makeStorage('files'), limits: { fileSize: 50 * 1024 * 1024 } });

app.post('/api/upload/book', uploadPdf.single('pdf'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'pdf is required' });

  const originalName = req.file.originalname;
  const bookTitle = sanitizeHtml(originalName, { allowedTags: [], allowedAttributes: {} }).trim() || 'Book';
  const bookId = makeIdFromName(originalName);

  const outRelDir = `/books/${bookId}`;
  const outAbsDir = path.join(PUBLIC_DIR, 'books', bookId);

  try {
    const parsed = await runPdfParser({
      pdfAbsPath: req.file.path,
      outAbsDir,
      title: bookTitle,
    });

    const pages = (parsed.pages || []).map((p) => ({
      page: p.page,
      url: `${outRelDir}/${p.file}`,
    }));

    const indexHtml = buildBookIndexHtml({ title: bookTitle, pages });
    fs.writeFileSync(path.join(outAbsDir, 'index.html'), indexHtml, 'utf8');

    const book = {
      id: bookId,
      title: bookTitle,
      createdAt: new Date().toISOString(),
      pdf: {
        name: originalName,
        url: `/uploads/pdfs/${req.file.filename}`,
      },
      indexUrl: `${outRelDir}/index.html`,
      pageCount: parsed.pageCount || pages.length,
      pages,
    };

    await booksStore.addBook(book);

    for (const p of pages) {
      await postsStore.addPost({
        title: `${bookTitle} — Page ${p.page}`,
        body: `<p>Auto-generated from <b>${bookTitle}</b>.</p><p><a href="${p.url}" target="_blank" rel="noreferrer">Open page ${p.page}</a></p>`,
      });
    }

    res.status(201).json({ book });
  } catch (err) {
    res.status(500).json({
      error: 'Failed to convert PDF to pages. Ensure Python + dependencies are installed.',
      details: err && err.details ? String(err.details).slice(0, 2000) : undefined,
    });
  }
});

app.post('/api/upload/video', uploadVideo.single('video'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'video is required' });
  res.status(201).json({ file: { url: `/uploads/videos/${req.file.filename}`, name: req.file.originalname } });
});

app.post('/api/upload/file', uploadFile.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'file is required' });
  res.status(201).json({ file: { url: `/uploads/files/${req.file.filename}`, name: req.file.originalname } });
});

app.get('/download/:kind/:filename', (req, res) => {
  const kind = req.params.kind;
  const filename = path.basename(req.params.filename);
  const allowed = new Set(['pdfs', 'videos', 'files']);
  if (!allowed.has(kind)) return res.status(400).send('Invalid kind');

  const abs = path.join(UPLOADS_DIR, kind, filename);
  if (!fs.existsSync(abs)) {
    return res.status(404).send('Not found');
  }

  res.download(abs);
});

// Contact endpoint (sanitized)
app.post('/api/contact', (req, res) => {
  const name = typeof req.body?.name === 'string' ? req.body.name : '';
  const email = typeof req.body?.email === 'string' ? req.body.email : '';
  const message = typeof req.body?.message === 'string' ? req.body.message : '';

  const cleanName = sanitizeHtml(name, { allowedTags: [], allowedAttributes: {} }).trim();
  const cleanEmail = sanitizeHtml(email, { allowedTags: [], allowedAttributes: {} }).trim();
  const cleanMessage = sanitizeHtml(message, { allowedTags: [], allowedAttributes: {} }).trim();

  if (!cleanName || !cleanEmail || !cleanMessage) {
    return res.status(400).json({ error: 'name, email, and message are required' });
  }

  res.json({ ok: true });
});

app.listen(PORT, () => {
  console.log(`Portfolio server running on http://localhost:${PORT}`);
});
