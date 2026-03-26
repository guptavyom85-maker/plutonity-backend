web: uvicorn app.main:app --host 0.0.0.0 --port 8000
worker: celery -A worker worker --loglevel=info