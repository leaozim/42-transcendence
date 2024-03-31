FROM python:3.11-alpine as builder

COPY ./requirements/local.txt ./requirements.txt

RUN apk add gcc musl-dev libffi-dev && \
    pip install -r requirements.txt --no-cache && \
    pip install gunicorn

FROM python:3.11-alpine as final

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/

WORKDIR transcendence

RUN apk add gettext && adduser -D app

COPY --chown=app:app . .

CMD ["python", "-m", "daphne", "srcs_core.asgi:application", "-p", "8001", "-b", "0.0.0.0"]

RUN chmod +x ./entrypoint.sh

EXPOSE 8000
EXPOSE 8001

USER app

CMD ./entrypoint.sh
