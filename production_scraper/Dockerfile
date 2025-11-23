FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV PYTHONUNBUFFERED=1
# default entrypoint can be overridden in k8s or docker-compose
CMD ["scrapy", "crawl", "robust"]
