import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "meinheld.gmeinheld.MeinheldWorker"
bind = "0.0.0.0:8000"
