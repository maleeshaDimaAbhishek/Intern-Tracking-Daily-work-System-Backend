# ── Base image ─────────────────────────────────────────────────
FROM python:3.11-slim

# ── Set working directory ──────────────────────────────────────
WORKDIR /app

# ── Install dependencies ───────────────────────────────────────
# Copy requirements first — Docker caches this layer
# so it won't reinstall unless requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy the rest of the backend code ─────────────────────────
COPY . .

# ── Create uploads folder ──────────────────────────────────────
RUN mkdir -p uploads/medical_certificates

# ── Expose the port FastAPI runs on ───────────────────────────
EXPOSE 8000

# ── Start the server ───────────────────────────────────────────
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
