FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/opt
ARG PROMTAIL_VERSION=2.8.6

RUN adduser --system --no-create-home cloudscraper-proxy
# Create a directory for supervisor socket file
RUN mkdir -p /var/run/supervisorctl && chown -R cloudscraper-proxy: /var/run/supervisorctl
# Install Promtail and supervisor.d
RUN apt-get update && apt-get install -y supervisor wget unzip build-essential && \
    wget -q https://github.com/grafana/loki/releases/download/v${PROMTAIL_VERSION}/promtail-linux-amd64.zip && \
    unzip promtail-linux-amd64.zip && \
    mv promtail-linux-amd64 /usr/local/bin/promtail && \
    rm promtail-linux-amd64.zip && \
    apt-get remove -y wget unzip && apt-get autoremove -y && apt-get clean

COPY service /opt/cloudscraper-proxy
COPY supervisord.conf /etc/supervisor/supervisord.conf
RUN mkdir -p /opt/cloudscraper-proxy/logs && chown -R cloudscraper-proxy: /opt/cloudscraper-proxy/logs

RUN pip install -r /opt/cloudscraper-proxy/requirements.txt

USER cloudscraper-proxy

CMD ["/usr/bin/supervisord"]
