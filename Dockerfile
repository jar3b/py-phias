FROM python:3.10.5-alpine3.16
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN apk add --no-cache \
        postgresql-dev \
        openssl \
    && apk add --no-cache --virtual .build-deps \
        build-base linux-headers git \
    && pip install --upgrade pip
ADD requirements.txt ./
RUN pip install -r requirements.txt && \
    pip install uvloop && \
    apk del .build-deps
ADD . .
RUN chmod a+x *.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "run.py", "8080"]