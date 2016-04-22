# py-phias
Python application that can operate with FIAS (Russian Address Object DB)

Простое приложение для работы с БД ФИАС, написано для Python 3, использует БД PostgreSQL
## Содержание
 - [Возможности](#Возможности)
 - [Установка](#Установка)
 - [Настройка](#Настройка)
 - [API](#Api)

## Возможности
1. API (выходной формат - JSON), основные функции которого:
    - Актуализация AOID, AOGUID.
    - Получение полного дерева адресного объекта по AOID.
    - Поиск адресного объекта по произвольной строке, выдает 10 самых релеватных результатов, может быть "мягким",
    с более широкими вариациями и исправлением опечаток (для подсказок), или "строгим" (к примеру, для автоматического 
    импорта из внешних систем).
2. Автоматическое развертывание базы ФИАС
    - Из директории с файлами XML (like 'AS_ADDROBJ_20160107_xxx.XML').
    - Из локального файла архива (.rar).
    - Напрямую с HTTP сервера ФНС.
3. Актуалиация базы (из XML, HTTP) с возможностью выбора необходимых обновлений.


## Установка
Протестирована работа на следующих ОС: [Windows](#windows) (8.1) и [Debian](#debian-linux) Jessie

### Зависимости

_Внимание_! Только Python 3 (для 2.7 пока есть отдельная ветка), только PostgreSQL, только Sphinx. MySQL/MariaDB, ElasticSearch/Solr
не поддерживаются и, скорее всего, не будут.
 
Для работы приложения необходимо достаточное кол-во RAM (1Gb+) и ~5.5Gb места на диске 
(3-3.5Gb для скачивания архива с базой, 350-400Mb для индексов Sphinx, 1Gb для базы). Также необходимы root права 
(администратора, для Windows), для работы searchd и предварительной установки. 
Рекомендую устанавливать или на отдельном сервере, или на своей машине, либо же на VPS. 
На shared хостинге работоспособность не гарантируется (только если хостер Вам сам все установит и настроит, 
и разрешит запуск демонов - читай: "невозможно")

Предварительно обязательно установить и настроить:

1. Python 3, pip
    Для Windows качаем - ставим, для Debian:
    ```
    sudo apt-get install python3-setuptools
    sudo easy_install3 pip
    sudo pip3 install --upgrade pip
    ```

2. PostgreSql 9.5 и выше (из-за синтаксиса _ON CONFLICT ... DO_)
    Для Windows, как обычно, [качаем](http://www.enterprisedb.com/products-services-training/pgdownload#windows) - ставим,
    для Debian 8 и ниже:
    ```
    sudo sh -c 'echo deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main 9.5 > /etc/apt/sources.list.d/postgresql.list'
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install postgresql-9.5
    ```
    , для Debian 9:
    `sudo apt-get install postgresql`

    Затем создайте пользователя и базу данных и установите расширение pg_trgm:
    ```
    sudo adduser --no-create-home fias
    sudo -u postgres psql
    postgres=# CREATE DATABASE fias_db;
    postgres=# CREATE USER fias WITH password 'fias';
    postgres=# GRANT ALL privileges ON DATABASE fias_db TO fias;
    postgres=# ALTER USER fias WITH SUPERUSER;
    postgres=# \q
    sudo -u fias psql -d fias_db -U fias
    postgres=# CREATE EXTENSION pg_trgm SCHEMA public;
    postgres=# \q
    ```

3. Sphinx 2.2.1 и новее:
    [Windows](http://sphinxsearch.com/downloads/release/), Debian:
    ```
    cd /tmp
    wget http://sphinxsearch.com/files/sphinx-2.2.10-release.tar.gz
    tar xzf sphinx-2.2.10-release.tar.gz
    cd sphinx-2.2.10-release
    sudo apt-get install postgresql-server-dev-9.5
    ./configure --without-mysql --with-pgsql
    make
    sudo make install
    ```
    , не забудте установить _build-essential_ перед этим (касается Debian).

4. Web-сервер с поддержкой WSGI, любой, по Вашему желанию.

### Windows
1. Установить lxml, скачав whl [отсюда](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml) и сделав
`pip install yourmodulename.whl`.
2. Есть некоторые проблемы с установкой и работой psycopg2 (Windows 10, VS 2015), если у Вас они присутствуют - качаем
[сборку для Windows](http://www.stickpeople.com/projects/python/win-psycopg/)
3. Установить unrar.exe (можно установить WinRar целиком).
4. Установить sphinxapi с поддержкой синтаксиса Python3:

    ```
    pip install https://github.com/jar3b/sphinx-py3-api/zipball/master
    ```

### Debian Linux
1. Установить unrar (non-free):

    ```
    sudo sh -c 'echo deb ftp://ftp.us.debian.org/debian/ <deb_name> main non-free > /etc/apt/sources.list.d/non-free.list'
    sudo apt-get update
    sudo apt-get install unrar
    ```

2. Устанавливаем и настраиваем libxml и виртуальное окружение:
    ```
    sudo apt-get install python3-lxml python3-dev
    sudo pip3 install virtualenv
    sudo virtualenv /opt/fias-env
    source /opt/fias-env/bin/activate
    ```
    Далее будем все устанавливать внутри virtualenv'a.

3. Установить sphinxapi с поддержкой синтаксиса Python3:

    ```
    pip install https://github.com/jar3b/sphinx-py3-api/zipball/master
    ```
### Общая часть:
Установим приложение из репозитория:

    ```
    cd /opt/fias-env
    sudo mkdir -p fias-api
    sudo chown fias: /opt/fias-env/fias-api
    sudo -u fias -H git clone --branch=py3 https://github.com/jar3b/py-phias.git fias-api
    cd fias-api
    sudo pip install -r requirements.txt
    ```

## Настройка
### Первоначальная настройка базы данных
1. Настроим конфиг, для этого необходимо изменить параметры в Вашем wsgi-entrypoint (в моем случае
[passenger_wsgi.py](passenger_wsgi.py)): в строке `from config import *` измените _config_ на имя Вашего
конфигурационного файла (создается рядом с wsgi app), пример конфига находится в файле
[config.example.py](config.example.py).
2. Создадим базу:
    - из архива `sudo -u phias python manage.py -b create -s /tmp/fias_xml.rar`
    - из директории `sudo -u phias python manage.py -b create -s /tmp/fias_xml_unpacked`
    - онлайн, с сервера ФНС `sudo -u phias python manage.py -b create -s http`
    - Также, можно указать конкретную версию ФИАС _только_ при http загрузке, с ключом `--update-version <num>`, где num -
номер версии ФИАС, все доступные версии можно получить, выполнив `manage.py -v`.

    Примечание 1: Если Вы инициализируете БД из архива или директории, при создании или обновлении базы у Вас будет
    запрошен номер устанавливаемой версии ФИАС.

    Примечание 2: У пользователя PostgreSql (postgres, либо созданного Вами) должны быть права на чтение из директории,
    указанной в `config.folders.temp`, иначе будет Permission denied при попытке bulk-import.
3. Проиндексируем Sphinx:
    - Windows: `python manage.py -c -i C:\sphinx\bin\indexer.exe -o C:\sphinx\sphinx.conf`
    - Debian: `sudo python manage.py -c -i indexer -o /usr/local/sphinx/etc/sphinx.conf`
4. Затем запустим searchd:
    - Windows: 
        - Устанавливаем службу: `C:\Sphinx\bin\searchd --install --config C:\Sphinx\sphinx.conf --servicename sphinxsearch`
        - и запускаем: `net start sphinxsearch`
    - Debian:
        - Запустим : `sudo searchd --config /usr/local/sphinx/etc/sphinx.conf`
        - если необходимо, добавьте `searchd --config /usr/local/sphinx/etc/sphinx.conf` в `/etc/rc.local` для автостарта
5. Настроим WSGI server, я использую nginx + passenger. Конфиг для passenger - [passenger_wsgi.py](passenger_wsgi.py),
конфиг для nginx - [py-phias.conf](https://gist.github.com/jar3b/f8f5d351e0ea8ae2ed8e). Вы можете
использовать любое приемлемое сочетание.

## Api

- `/normalize/<guid>` - актуализирует AOID или AOGUID, на выходе выдает

  `{"aoid": "1d6185b5-25a6-4fe8-9208-e7ddd281926a"}`, где aoid - актуальный AOID.
- `/find/<text>` и `/find/<text>/strong`- полнотекстовый поиск по названию адресного объекта. `<text>` - строка поиска.
Если указан параметр `strong`, то поиск будет выдавать меньше результатов, но они будут точнее. Если же флаг не
указан, но будет выдано 10 наиболее релевантных результатов.

    На выходе будет массив:
    ```
    [
      {
        "cort": 0,
        "text": "обл Псковская, р-н Порховский, д Гречушанка",
        "ratio": 1537,
        "aoid": "1d6185b5-25a6-4fe8-9208-e7ddd281926a"
      },
      ... (up to 10)
    ]
    ```
    ,где cort - количество несовпавших слов, text - полное название адресного объекта, ratio - рейтинг, aoid -
    актуальный AOID.