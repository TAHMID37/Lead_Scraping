# ── Stage 1: Build React frontend ────────────────────────────────────────────
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --frozen-lockfile 2>/dev/null || npm install

COPY frontend/ .
# In production the frontend uses relative URLs, so API_BASE_URL = ''
ENV REACT_APP_API_URL=""
RUN npm run build

# ── Stage 2: Python backend + static frontend ────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built React app from stage 1
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Environment (override these at runtime via -e or --env-file)
ENV SPIDER_API_KEY=""
ENV GEMINI_API_KEY=""
ENV HUBSPOT_API_KEY=""
ENV DATA_DIR="/app/backend/data"

RUN mkdir -p /app/backend/data

WORKDIR /app/backend

EXPOSE 3001

CMD ["uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "3001"]
