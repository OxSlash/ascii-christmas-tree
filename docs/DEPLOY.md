# Deploy guide

The browser build is a static site: `public/` contains everything a host needs, so
Vercel does not have to run Python during deployment.

## 1. Build the site

From the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python tools/build_web.py
```

On macOS or Linux use `source .venv/bin/activate`. The script runs pygbag and copies
`web/build/web` into `public/`, then applies a small dark-background style to
`index.html`.

## 2. Test it locally

```bash
python -m http.server 8000 --directory public
```

Open <http://localhost:8000>. The first load downloads the Python runtime from the
pygbag CDN, so give it a few seconds. The page asks for a click before starting; that
is normal.

## 3. Publish the source

Create an empty public repository named `ascii-christmas-tree` on GitHub, then from the
repository root:

```bash
git init
git add .
git commit -m "ASCII Christmas Tree"
git branch -M main
git remote add origin https://github.com/<your-user>/ascii-christmas-tree.git
git push -u origin main
```

`memory/`, `task.md`, `.venv/`, `web/build/`, and `web-cache/` are already ignored.

## 4. Deploy on Vercel

1. Sign in at <https://vercel.com> with the same GitHub account.
2. Choose **Add New → Project** and import `ascii-christmas-tree`.
3. Framework preset: **Other**. Build command: leave empty. Output directory:
   `public` (also set in `vercel.json`).
4. Press **Deploy**. The first build finishes in under a minute because there is
   nothing to compile.

Every later push to `main` redeploys automatically. To publish a new visual change,
run `python tools/build_web.py` again, commit the updated `public/` folder, and push.

## Troubleshooting

- **Blank page or endless loading:** open the browser console. A blocked request to
  `pygame-web.github.io` means the CDN is unreachable from that network.
- **Slow first load:** the Python 3.12 runtime is about 11 MB and is cached by the
  browser afterwards.
- **Old version still showing:** hard refresh with `Ctrl+F5`; the CDN runtime is
  cached aggressively.
