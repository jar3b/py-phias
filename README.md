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

2. Устанавливаем и настраиваем libxml:
    ```
    sudo apt-get install libxml2-dev libxslt1-dev python3-dev python3-lxml
    ```

3. Установить sphinxapi с поддержкой синтаксиса Python3:

    ```
    sudo pip3 install https://github.com/jar3b/sphinx-py3-api/zipball/master
    ```
### Общая часть:
1. Установим приложение из репозитория:

    ```
    cd /var/www/
    sudo mkdir -p fias-api
    sudo chown fias: /var/www/fias-api
    sudo -H -u fias git clone --branch=py3 https://github.com/jar3b/py-phias.git fias-api
    cd fias-api
    sudo pip3 install -r requirements.txt
    ```
2. Иные пути установки ... (soon)

## Настройка
### Первоначальная настройка базы данных
1. Настроим конфиг, для этого необходимо изменить параметры в Вашем wsgi-entrypoint (в моем случае
[wsgi.py](wsgi.py)): в строке `from config import *` измените _config_ на имя Вашего
конфигурационного файла (создается рядом с wsgi app), пример конфига находится в файле
[config.example.py](config.example.py).
2. Создадим базу:
    - из архива `sudo -u fias python3 manage.py -b create -s /tmp/fias_xml.rar`
    - из директории `sudo -u fias python3 manage.py -b create -s /tmp/fias_xml_unpacked`
    - онлайн, с сервера ФНС `sudo -u fias python3 manage.py -b create -s http`
    - Также, можно указать конкретную версию ФИАС _только_ при http загрузке, с ключом `--update-version <num>`, где num -
номер версии ФИАС, все доступные версии можно получить, выполнив `manage.py -v`.

    Примечание 1: Если Вы инициализируете БД из архива или директории, при создании или обновлении базы у Вас будет
    запрошен номер устанавливаемой версии ФИАС.

    Примечание 2: У пользователя PostgreSql (postgres, либо созданного Вами) должны быть права на чтение из директории,
    указанной в `config.folders.temp`, иначе будет Permission denied при попытке bulk-import.
3. Проиндексируем Sphinx:
    - Windows: `python manage.py -c -i C:\sphinx\bin\indexer.exe -o C:\sphinx\sphinx.conf`
    - Debian: `sudo python3 manage.py -c -i indexer -o /usr/local/etc/sphinx.conf`
4. Затем запустим searchd:
    - Windows: 
        - Устанавливаем службу: `C:\Sphinx\bin\searchd --install --config C:\Sphinx\sphinx.conf --servicename sphinxsearch`
        - и запускаем: `net start sphinxsearch`
    - Debian:
        - Запустим : `sudo searchd --config /usr/local/etc/sphinx.conf`
        - если необходимо, добавьте `searchd --config /usr/local/etc/sphinx.conf` в `/etc/rc.local` для автостарта
5. Для проверки работы выполните `sudo -H -u fias python3 passenger_wsgi.py`, по адресу
`http://example.com:8087/find/москва`
Вы должны увидеть результаты запроса.

### Установка Web-сервера (для Debian, на примере nginx + gunicorn, без virtualenv)
- Установим nginx и gunicorn:

    ```
    sudo apt-get install nginx
    sudo pip3 install gunicorn
    ```
- По пути с приложением отредактируйте файл [gunicorn.conf.py](gunicorn.conf.py)
- Настройте nginx. Примерно так:

    ```
    cd /etc/nginx/sites-available
    sudo wget -O fias-api.conf https://gist.githubusercontent.com/jar3b/f8f5d351e0ea8ae2ed8e/raw/2f1b0d2a6f9ce9db017117993954158ccce049dd/py-phias.conf
    sudo nano fias-api.conf
    ```
    , отредактируйте и сохраните файл, затем оздайте линк

    ```
    sudo cp -l fias-api.conf ../sites-enabled/fias-api.conf
    ```
- Запустим gunicorn (пока без демона, для теста) и nginx:

    ```
    cd /var/www/fias-api
    sudo gunicorn -c gunicorn.conf.py wsgi:application &
    sudo service nginx start
    ```
- В пристейшем случае Ваш `/etc/rc.local` может выглядеть так, как ниже. Лмбо используйте аналоги supervisor.

    ```
    searchd --config /usr/local/etc/sphinx.conf
    cd /var/www/fias-api
    gunicorn -c gunicorn.conf.py wsgi:application &

    exit 0
    ```

## Api

- `/normalize/<guid>` - актуализирует AOID или AOGUID, на выходе выдает

  ```
  {"aoid": "1d6185b5-25a6-4fe8-9208-e7ddd281926a"}
  ```

  , где _aoid_ - актуальный AOID.
- `/find/<text>?strong=<0,1>`- полнотекстовый поиск по названию адресного объекта. `<text>` - строка поиска.
Если указан параметр `strong=1`, то в массиве будет один результат, или ошибка. Если же флаг не указан, но будет выдано 10
наиболее релевантных результатов.

    На выходе будет массив от 1 до 10 элементов:
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
    ,где _cort_ - количество несовпавших слов, _text_ - полное название адресного объекта, _ratio_ - рейтинг, _aoid_ -
    актуальный AOID.
- `/expand/<aoid>` - "раскрывает" AOID, возвращая массив адресных элементов. `<aoid>` - актуальный или неактуальный
AOID

    На выходе будет массив из адресных элементов, упорядоченный по AOLEVEL:
    ```
    [
      {
        "aoguid": "0c5b2444-70a0-4932-980c-b4dc0d3f02b5",
        "shortname": "г",
        "aoid": "5c8b06f1-518e-496e-b683-7bf917e0d70b",
        "formalname": "Москва",
        "aolevel": 1,
        "socrname": "Город",
        "regioncode": 77
      },
      {
        "aoguid": "10409e98-eb2d-4a52-acdd-7166ca7e0e48",
        "shortname": "п",
        "aoid": "41451677-aad4-4cb9-ba76-2b0eeb156acb",
        "formalname": "Вороновское",
        "aolevel": 3,
        "socrname": "Поселок",
        "regioncode": 77
      },
      {
        "aoguid": "266485f4-a204-4382-93ce-7a47ad934869",
        "shortname": "ул",
        "aoid": "943c8b81-2491-46ee-aee4-48d0c9fada1a",
        "formalname": "Новая",
        "aolevel": 7,
        "socrname": "Улица",
        "regioncode": 77
      }
    ]
    ```
    , все поля из таблицы ADDROBJ.
- `/gettext/<aoid>` - возвращает текст для произвольного _aoid_, тект аналогичен тому, который возвращает `/find/<text>`,
на выходе будет такой массив с одним элементом:

    ```
    [
      {
        "fullname": "г Москва, п Вороновское, п ЛМС, ул Новая"
      }
    ]
    ```
- Ошибки. Если при выполнении запроса произошла ошибка, то ответ будет таким, объект с одним полем описания ошибки:

    ```
    {
      "error": "'Cannot find sentence.'"
    }
    ```