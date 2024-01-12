FROM python:3.11-alpine

WORKDIR transcendence

COPY ./requirements/local.txt ./requirements.txt


RUN pip install pip --upgrade; \
    pip install -r requirements.txt; \
    rm requirements.txt; \
    adduser -D app

COPY --chown=app:app . .

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

USER app

ENTRYPOINT ./entrypoint.sh
