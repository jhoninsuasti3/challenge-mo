#!/bin/bash

uvicorn api.main:app --host 0.0.0.0 --port 80 &

celery -A api.celery_config worker -l info -P eventlet --concurrency=2 -Q queue_total_purchases -E -n total_purchases &

exec "$@"