FROM python:3.10.5-alpine3.16
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN apk add --no-cache \
        postgresql-dev \
        openssl \
    && apk add --no-cache --virtual .build-deps \
        build-base linux-headers git \
    && pip install --upgrade pip
ADD requirements.txt requirements_dev.txt ./libs/ ./
RUN pip install -r requirements.txt && pip install uvloop-0.16.0-cp310-cp310-linux_x86_64.whl
RUN apk del .build-deps \
    && rm *.whl
ADD . .
RUN rm -rf libs

CMD ["python", "run.py", "8080"]