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

## 2. Hugging Face Spaces (live demo — free, no card)

1. Go to **huggingface.co/new-space**.
2. **Space name:** `candora` · **SDK:** **Docker** · **Hardware:** CPU basic (free).
3. Create the Space. It gives you a git URL like `https://huggingface.co/spaces/<you>/candora`.
4. Add your Groq key as a **secret** (Space → Settings → Variables and secrets → New secret):
   - Name: `GROQ_API_KEY` · Value: *your key*
5. Push the code to the Space:

```bash
git remote add space https://huggingface.co/spaces/<you>/candora
git push space main
```

The Space builds the `Dockerfile` (React build → served by FastAPI on port 7860). First build takes ~5–10 min. When it's live, the app auto-seeds the demo documents on startup, so it's usable immediately.

> **Auth for the push:** when prompted, use your HF username and an **access token** (huggingface.co/settings/tokens, role `write`) as the password.

---

## Updating after changes

```bash
git add -A && git commit -m "..."
git push origin main    # GitHub
git push space main     # redeploy on HF Spaces
```

---

## Local single-service (mirror of production)

```bash
cd frontend && npm run build
cd .. && uvicorn api.main:app --port 8000    # serves UI + API at http://localhost:8000
```
