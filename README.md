# py-phias

Python application that can operate with FIAS (Russian Address Object DB)

Простое приложение для работы с БД ФИАС, используя БД PostgreSQL + Sphinxsearch. ГАР не поддерживается,
только ФИАС в старом формате, последняя база от 31.08.2021

![Пример работы](https://github.com/jar3b/py-phias/raw/gh-pages/static/example.mp4)

Swagger: [github-pages](https://jar3b.github.io/py-phias/)

## Содержание

- [Возможности](#Возможности)
- [Установка](#Установка)
- [API](#Api)

## Возможности

1. API (выходной формат - JSON), основные функции которого:
    - Актуализация AOID, AOGUID.
    - Получение полного дерева адресного объекта по AOID.
    - Поиск адресного объекта по произвольной строке, выдает 10 самых релеватных результатов, может быть "мягким",
      с более широкими вариациями и исправлением опечаток (для подсказок), или "строгим" (к примеру, для автоматического
      импорта из внешних систем).
    - **ВНИМАНИЕ**: Поиск объекта только до улицы, **по домам** и квартирам **не ищет**! Поддержки нет и в рамках этого
      проекта не будет точно.

2. Автоматическое развертывание базы ФИАС
    - Из директории с файлами XML, распакованными из архива с сайта ФНС (напр. `AS_ADDROBJ_20160107_xxx.XML`)
    - Из предподготовленных данных в формате `CSV`

## Установка

ОС Linux, x86_64, Docker. Требования по "железу":

- Диск: ~4Гб (БД + индексы + образы докера). Опционально сюда добавляется архив с базой (14Гб) + распакованная база
  (до 60Гб, но можно распаковывать не все файлы, ниже есть об этом).
- RAM: 512Mb на Sphinx и примерно еще столько же на приложение + Postgres. 1Гб должно хватить минимально, в противном
  случае можно подтюнить [sphinx.conf:5](orchestra/templates/sphinx.conf)

Далее будет описана установка для Ubuntu 20.04 на VPS, но возможно использовать и другой дистрибутив.

### Зависимости

Обязательна установка Docker, docker-compose. Можете по инструкции c 
[офф. сайта](https://docs.docker.com/engine/install/ubuntu/), либо по такой:

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### Подготовка и скачивание компонентов ПО

Копируем на удаленный хост файлы из папки `deploy`: [.env](deploy/.env),
[docker-compose.yml](deploy/docker-compose.yml), [init.sh](deploy/init.sh)

Далее настраиваем файл `.env` (можно и не менять), пример:

```dotenv
DB_USER=admin
DB_PASS=devpass
DB_NAME=fias
DB_HOST=db
DB_PORT=5432
# директория, в которой будут хранится индексы сфинкса
SPHINX_VAR=/var/lib/sphinxsearch
# порт прослушки, важно, если SHPINX_LISTEN представляет собой TCP сокет, а не юникс
SPHINX_PORT=9312
# что слушает сфинкс, 'shpinx:9312' для TCP (где 'shpinx' - это имя контейнера) или '/temp/fias.sock'
# для юникс-сокета
SHPINX_LISTEN=/temp/fias.sock
```

### Загрузка исходных данных

Есть 2 варианта загрузки:

- Из распакованного архива с сайта ФНС.
- Из предподготовленных данных в формате `CSV`.

#### Загрузка из распакованного архива с сайта ФНС

Идем в [архив](https://fias.nalog.ru/DataArchive) и качаем любую из `ПОЛНАЯ БД ФИАС - XML`, там будет архив под 12Гб.
Его либо распаковываем на виртуалке и кладем файлы в `./data/source`, либо качаем на свою машину, а файлы заливаем по
SFTP. Заливать все файлы необходимости нет, нужны 2 таблицы: `ADDROBJ` и `SOCRBASE`, итого `ls -la ./data/source`
после всех этих манимуляций должна выглядеть как-то так:

```
$ ls -la
drwxr-xr-x 1 user user          0 Jul 16 01:22 ./
drwxr-xr-x 1 user user          0 Jul 19 19:34 ../
-rw-r--r-- 1 user user 3882354436 Sep  1  2021 AS_ADDROBJ_20210901_34d43f4d-f8a9-4aff-a446-9696e9908011.XML
-rw-r--r-- 1 user user      39012 Sep  1  2021 AS_SOCRBASE_20210901_d242a252-db1f-4492-afd6-78af81f0588d.XML
```

#### Загрузка пред-подготовленных данных в формате `CSV`

Есть другой вариант, скачать уже подготовленные мной данные, это выгрузка от 31.08.2021 (последняя) в формате,
который предварительно подготовлен и который поддерживается программой. Скачать можно с
[Яндекс Диска](https://disk.yandex.ru/d/AKQR8DEIcVKeSw), заливать придется по SFTP, при этом **распаковывать** архив
этот уже **не надо**; в таком случае папка будет как-то так выглядеть:

```
$ ls -la ./data/source
total 215616
drwxrwxr-x 2 user user      4096 Jul 19 22:45 .
drwxrwxr-x 3 user user      4096 Jul 19 22:37 ..
-rw-rw-r-- 1 user user 220779247 Jul 19 22:46 fias_csv_31_08_2021.zip
```

### Популяция базы, индексирование и старт

Далее можно просто выполнить `sudo ./init.sh`, глянуть можно здесь ([init.sh](deploy/init.sh)). После этого можно
очистить исходники базы, они больше не нужны (`sudo rm -rf ./data/source/*`)

### TLS-termination и NGINX

Тут много всего описано в интернете, конфиг nginx примерно такой:

```
upstream fias {
    server 127.0.0.1:8080 fail_timeout=0;
}

server {
    if ($host = fias.example.org) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    listen [::]:80;
    server_name fias.example.org;

    location / {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_redirect off;
      proxy_pass http://fias;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name fias.example.org;
    server_tokens off;
    client_max_body_size 1M;
    keepalive_timeout 5;

    # certs sent to the client in SERVER HELLO are concatenated in ssl_certificate
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Diffie-Hellman parameter for DHE ciphersuites, recommended 2048 bits
    # ssl_dhparam /etc/ssl/certs/dhparam.pem;

    # modern configuration. tweak to your needs.
    ssl_protocols TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256';
    ssl_prefer_server_ciphers on;

    # HSTS (ngx_http_headers_module is required) (15768000 seconds = 6 months)
    add_header Strict-Transport-Security max-age=15768000;

    # OCSP Stapling ---
    # fetch OCSP records from URL in ssl_certificate and cache them
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;

    location ^~ /.well-known/acme-challenge/ {
      alias /var/www/html;
    }

    location / {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_set_header X-Forwarded-Proto https;
      proxy_redirect off;
      proxy_pass http://fias;
    }
    ssl_certificate /etc/letsencrypt/live/fias.example.org/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/fias.example.org/privkey.pem;
 # managed by Certbot
}
```

Тут важна больше всего опция `proxy_set_header X-Forwarded-Proto https;`, чтобы нормально отображался сваггер. Также, в
`docker-compose.yml` потом можно поставить порты в `app`, чтобы слушало только `localhost`.

## Api

После старта приложения по адресу: `http://{ip}:8080/docs` будет доступен Swagger с описанием и возможностью 
тестировать запросы на реальном окружении. Также его можно глянуть на [github-pages](https://jar3b.github.io/py-phias/),
результаты отдавать не будет, естественно.
