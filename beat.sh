#!/bin/sh

set -o errexit
set -o nounset

celery -A core beat -l info
exec "$@"