FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --gid 10001 harbor && useradd --uid 10001 --gid harbor --no-create-home harbor \
    && mkdir /data && chown harbor:harbor /data
COPY requirements.lock ./
RUN python -m pip install --no-cache-dir -r requirements.lock
COPY harbor_grc ./harbor_grc
USER 10001:10001
ENV GRC_DATABASE=/data/harbor.db
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
  CMD python -c "import os,urllib.request; from urllib.parse import urlsplit; req=urllib.request.Request('http://127.0.0.1:8000/health/ready',headers={'Host':urlsplit(os.environ['GRC_ORIGIN']).netloc}); urllib.request.urlopen(req,timeout=3)" || exit 1
CMD ["python", "-m", "harbor_grc", "serve", "--host", "0.0.0.0"]

