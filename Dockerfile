# --- Stage 1: build the React frontend ---
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python backend serving the built frontend ---
FROM python:3.11-slim
WORKDIR /app

# System deps kept minimal; onnxruntime wheels are self-contained.
ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.cache/huggingface \
    CHROMA_CACHE_DIR=/app/.cache/chroma

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the local ONNX embedding model so first request is fast.
RUN python -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction; DefaultEmbeddingFunction()(['warmup'])"

# Backend source
COPY api/ ./api/
COPY agent/ ./agent/
COPY ingestion/ ./ingestion/
COPY evaluation/ ./evaluation/
COPY models/ ./models/
COPY config.py ./
COPY test_data/ ./test_data/

# Built frontend from stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Default port; hosts that inject $PORT (Render, Koyeb, Fly.io, …) override it.
ENV PORT=7860
EXPOSE 7860

CMD ["python", "-m", "api.main"]
