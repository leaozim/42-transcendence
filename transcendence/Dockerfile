FROM python:3.11-alpine as builder

COPY ./requirements/local.txt ./requirements.txt

RUN apk add gcc musl-dev libffi-dev; \
    pip install -r requirements.txt --no-cache


FROM python:3.11-alpine as final

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

WORKDIR transcendence

RUN apk add gettext; \
    chmod -R 777 /transcendence/coverage ; \
    adduser -D app

COPY --chown=app:app . .

CMD ["daphne", "src_core.asgi:application", "-u", "transcendence/daphne.sock"]

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

USER app

ENTRYPOINT ./entrypoint.sh
