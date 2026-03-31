# ---------- Stage 1: Base image ----------
FROM python:3.11-slim

# ---------- Stage 2: Set working directory ----------
WORKDIR /app

# ---------- Stage 3: Install dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Stage 4: Copy application code ----------
COPY app/ ./app/

# ---------- Stage 5: Expose port ----------
EXPOSE 8000

# ---------- Stage 6: Start the server ----------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
