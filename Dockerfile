# Stage 1: build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app

# Install system packages needed to compile native extensions
RUN apt-get update && \
    apt-get install -y build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the entire project into the builder
COPY . /app

# Install Poetry and runtime dependencies only (do not install the project package)
RUN pip install --upgrade pip poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-root

# Stage 2: runtime image
FROM python:3.11-slim
WORKDIR /app

# Ensure Python outputs are unbuffered and disable Poetry venvs
ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    DATABASE_URL="sqlite:///./book_exchange.db"

# Copy installed libraries and executables from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages \
                  /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code into the runtime image
COPY . /app

# Expose port 8000 for Uvicorn
EXPOSE 8000

# Launch the app via Uvicorn against flat main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
