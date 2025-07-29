# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

ARG REQUIREMENTS=requirements.txt
COPY requirements.txt /app/requirements.txt
COPY requirements-dev.txt /app/requirements-dev.txt

RUN pip install --no-cache-dir -r ${REQUIREMENTS}

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
