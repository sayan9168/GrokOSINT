FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends dnsutils whois && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir holehe maigret ignorant 2>/dev/null || true
COPY . .
EXPOSE 5000
ENV PYTHONUNBUFFERED=1
CMD ["python", "web_app.py"]
