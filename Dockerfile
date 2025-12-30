FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ARG APP_MODULE=apps.portal
ENV APP_MODULE=${APP_MODULE}
ENV PORT=8050

CMD ["sh", "-c", "python -m ${APP_MODULE}"]
