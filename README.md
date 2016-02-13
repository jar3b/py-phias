# py-phias
Python application that can operate with FIAS (Russian Address Object DB)

Простое приложение для работы с БД ФИАС, написано для Python 2.7, использует БД PostgreSQL

## Возможности
1. API (выходной формат - JSON), основные функции которого:
    - Актуализация AOID, AOGUID.
    - Получение полного дерева адресного объекта по AOID.
    - Поиск адресного объекта по произвольной строке, выдает 10 самых релеватных результатов, может быть "мягким",
    с более широкими вариациями и исправлением опечаток (для подсказок), или "строгим" (к примеру, для автоматического 
    импорта из внешних систем).
2. Автоматическое развертывание базы ФИАС
    - Из директории с файлами XML (like 'AS_ADDROBJ_20160107_xxx.XML').
    - Напрямую с HTTP сервера ФНС.
3. Актуалиация базы (из XML, HTTP) с возможностью выбора необходимых обновлений.


## Установка
Протестирована работа на следующих ОС: [Windows](#windows) (8.1) и [Debian](#debian-linux) Jessie

### Зависимости

_Внимание_! Только Python 2.7, только PostgreSQL, только Sphinx. Python 3, MySQL/MariaDB, Lucene/Solr не
поддерживаются и не будут.
 
Для работы приложения необходимо достаточное кол-во RAM (1Gb+) и 4.5Gb места на диске 
(3-3.5Gb для скачивания архива с базой и  300-400Mb для индексов Sphinx). Также необходимы root права 
(Администратора, для OS Windows), для работы searchd и предварительной установки. 
Рекомендую устанавливать или на отдельном сервере, или на своей машине, либо же на VPS. 
На shared хостинге работоспособность не гарантируется (только если хостер Вам сам все установит и настроит, 
и разрешит запуск демонов - читай: "невозможно")

Предварительно обязательно установить и настроить:

1. Python 2.7.x, pip
Для Windows качаем - ставим, для Debian:
```
sudo apt-get install python-setuptools
sudo easy_install pip
sudo pip install --upgrade pip 
```
2. PostgreSql 9.5 и выше (из-за синтаксиса _ON CONFLICT ... DO_)
Для Windows, как обычно, [качаем](http://www.enterprisedb.com/products-services-training/pgdownload#windows) - ставим, для Debian:
```
sudo sh -c 'echo deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main 9.5 > /etc/apt/sources.list.d/postgresql.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install postgresql-9.5
```
Затем создайте пользователя и базу данных.
3. Sphinx 2.2.1 и новее:
[Windows](http://sphinxsearch.com/downloads/release/), Debian:
```
cd /tmp
wget http://sphinxsearch.com/files/sphinx-2.2.10-release.tar.gz
tar xzf sphinx-2.2.10-release.tar.gz
cd sphinx-2.2.10-release
sudo apt-get install  postgresql-server-dev-9.5
./configure --without-mysql --with-pgsql
make
sudo make install
```
4. Web-сервер с поддержкой WSGI, любой, по Вашему желанию.

### Windows
1. Установить lxml, через pip не ставится, так что качаем [отсюда](https://pypi.python.org/pypi/lxml/3.5.0).
2. Установить unrar.exe (можно установить WinRar целиком).
3. Установить sphinxapi последней версии (либо взять из директории Sphinx): 
```
python -m pip install https://github.com/Romamo/sphinxapi/zipball/master
```


### Debian Linux
1. Установить libxml
```
sudo apt-get install python-dev libxml2 libxml2-dev libxslt-dev
```
1. Установить unrar (non-free)
```
sudo sh -c 'echo deb ftp://ftp.us.debian.org/debian/ stable main non-free > /etc/apt/sources.list.d/non-free.list'
sudo apt-get update
sudo apt-get install unrar
```
2. Установить sphinxapi последней версии: 
```
pip install https://github.com/Romamo/sphinxapi/zipball/master
```
3. Установить, собственно, нашу штуку:
```
pip install --target=d:\somewhere\other\than\the\default https://github.com/jar3b/...
```