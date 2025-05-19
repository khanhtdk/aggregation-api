# Build stage
FROM python:3.12-alpine AS builder
RUN apk update && apk add --no-cache gcc python3-dev musl-dev linux-headers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir wheels -r requirements.txt


# Main stage
FROM python:3.12-alpine
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels
WORKDIR /app
COPY . .
EXPOSE 5000
CMD ["uwsgi", "--ini", "uwsgi.ini"]
