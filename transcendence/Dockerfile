FROM python:3.11-alpine

WORKDIR transcendence

COPY ./requirements/local.txt ./requirements.txt

ENV PATH="/venv/bin:$PATH"

RUN apk add gettext; \
	pip install pip --upgrade; \
    pip install -r requirements.txt; \
    rm requirements.txt; \
    chmod -R 777 /transcendence/coverage ; \
    adduser -D app

COPY --chown=app:app . .

CMD ["daphne", "src_core.asgi:application", "-u", "transcendence/daphne.sock"]

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

USER app

ENTRYPOINT ./entrypoint.sh