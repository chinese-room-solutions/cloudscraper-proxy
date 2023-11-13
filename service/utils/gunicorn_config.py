import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
keepalive = 10
logger_class = "utils.gunicorn_structlog.GunicornLogger"
