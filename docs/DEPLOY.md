# Deployment Guide

Two targets: **GitHub** (mandatory repo) and **Hugging Face Spaces** (the live "working link"). Same code, two remotes.

---

## 1. GitHub (code repository)

Create an empty repo on github.com (no README/gitignore — this project already has them), then:

```bash
git remote add origin https://github.com/<you>/candora.git
git branch -M main
git push -u origin main
```

> The `.gitignore` already excludes `.env`, `.venv/`, `chroma_db/`, `logs/`, and `node_modules/`. **Your API key is never committed** — verify with `git ls-files | grep .env` (should show only `.env.example`).

---

## 2. Render (live demo — free, no card, deploys from GitHub)

> Hugging Face Docker Spaces now require a paid plan, so we use Render's free web-service tier. It builds our `Dockerfile` straight from the GitHub repo.

1. Go to **render.com** → sign up (GitHub login is easiest) → **New +** → **Web Service**.
2. Connect the **`candora`** GitHub repo.
3. Render auto-detects the `Dockerfile`. Settings:
   - **Environment:** Docker
   - **Instance type:** **Free**
   - **Region:** closest to you
4. Add an environment variable:
   - Key: `GROQ_API_KEY` · Value: *your Groq key*
5. **Create Web Service.** First build takes ~5–10 min. The app binds Render's `$PORT` automatically and auto-seeds the demo documents on startup, so it's usable immediately.

> **Free-tier note:** the service sleeps after ~15 min idle and cold-starts (~1 min) on the next visit. **Wake it a minute before demoing.**

Other Docker hosts (Koyeb, Fly.io, a VM) work identically — point them at the `Dockerfile` and set `GROQ_API_KEY`.

---

## Updating after changes

```bash
git add -A && git commit -m "..."
git push origin main    # GitHub — Render auto-redeploys on push
```

---

## Local single-service (mirror of production)

```bash
cd frontend && npm run build
cd .. && uvicorn api.main:app --port 8000    # serves UI + API at http://localhost:8000
```
