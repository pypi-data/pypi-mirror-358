FROM python:3.12-slim

WORKDIR /app

ARG REQUIREMENTS=requirements.txt
COPY requirements.txt /app/requirements.txt
COPY requirements-dev.txt /app/requirements-dev.txt

# Install build dependencies for Python packages (libsas)
RUN apt-get update && apt-get install -y build-essential python3-dev

RUN pip install --no-cache-dir -r ${REQUIREMENTS}

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
