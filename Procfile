web: daphne HabbitBackend.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: celery -A HabbitBackend worker -B -l info
