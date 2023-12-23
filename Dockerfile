FROM python:3.12-slim-bookworm as builder

ENV DEBIAN_FRONTEND=noninteractive
ARG PROMTAIL_VERSION=2.8.6

# Install build dependencies
RUN apt-get update && apt-get install -y wget unzip build-essential

# Download and install Promtail
RUN wget -q https://github.com/grafana/loki/releases/download/v${PROMTAIL_VERSION}/promtail-linux-amd64.zip && \
    unzip promtail-linux-amd64.zip && \
    mv promtail-linux-amd64 /usr/local/bin/promtail && \
    rm promtail-linux-amd64.zip

# Copy the service and install Python dependencies
COPY service /opt/cloudscraper-proxy
RUN pip wheel -w /wheels -r /opt/cloudscraper-proxy/requirements.txt

FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/opt

RUN adduser --system --no-create-home cloudscraper-proxy

# Create a directory for supervisor socket file
RUN mkdir -p /var/run/supervisorctl && chown -R cloudscraper-proxy: /var/run/supervisorctl

# Install supervisor.d and copy Promtail from the builder stage
RUN apt-get update && apt-get install -y supervisor && apt-get clean
COPY --from=builder /usr/local/bin/promtail /usr/local/bin/promtail

# Copy the service and Python wheels from the builder stage
COPY --from=builder /wheels /wheels
COPY service /opt/cloudscraper-proxy
COPY supervisord.conf /etc/supervisor/supervisord.conf
RUN mkdir -p /opt/cloudscraper-proxy/logs && chown -R cloudscraper-proxy: /opt/cloudscraper-proxy

# Install Python dependencies using the pre-built wheels
RUN pip install --no-index --find-links=/wheels -r /opt/cloudscraper-proxy/requirements.txt && rm -rf /wheels

USER cloudscraper-proxy
EXPOSE 5000

CMD ["/usr/bin/supervisord"]
