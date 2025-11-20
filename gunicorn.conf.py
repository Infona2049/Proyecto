import multiprocessing
import os

# Gunicorn config variables
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
keepalive = 5
timeout = 120

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Directories
chdir = '/opt/render/project/src'
