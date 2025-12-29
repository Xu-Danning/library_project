FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# 安装系统依赖（如需要）
RUN apt-get update && apt-get install -y --no-install-recommends gcc libmariadb-dev-compat libmariadb-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "python wait_for_db.py && gunicorn -b 0.0.0.0:5000 app:app"]
