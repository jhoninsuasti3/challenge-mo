#!/usr/bin/env bash
alembic upgrade heads
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
