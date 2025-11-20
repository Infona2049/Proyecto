import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Worker processes
workers = 2
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
keepalive = 5
timeout = 120

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
