#!/bin/bash

set -o errexit
set -o nounset

rm -rf celerybeat-schedule
celery -A core worker -B -l INFO
# python /tmp/debugpy --listen 0.0.0.0:6900 -m celery -A core worker -l INFO
exec "$@"