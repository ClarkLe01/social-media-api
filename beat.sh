#!/bin/sh

set -o errexit
set -o nounset

celery -A core beat -l info -s /home/app/backend/celerybeat-schedule