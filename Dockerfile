FROM python:3.12-slim

WORKDIR /app

# Install dependencies for SQLAlchemy and PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Run the application and use port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

