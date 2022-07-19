# py-phias

Python application that can operate with FIAS (Russian Address Object DB)

Простое приложение для работы с БД ФИАС, используя БД PostgreSQL + Sphinxsearch. ГАР не поддерживается,
только ФИАС в старом формате, последняя база от 31.08.2021

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

## Установка

Должно устанавливаться везде, где есть докер. Требуемое свободное рабочее пространство ~4Гб (БД + индексы + образы
докера).
Опционально сюда добавляется архив с базой (14Гб) + распакованная база (до 60Гб, но можно распаковывать не все файлы).

Далее будет описана установка для Ubuntu 20.04 на VDS, но возможно использовать и любой другой дистрибутив.

### Зависимости

Обязательна установка Docker, docker-compose. Можете с офф сайта, или такие инструкции:

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

### Подготовка и скачивание исходных данных

1. Сборка образов. Для этого нужно в корне проекта запустить `./make.sh`, если хост под Windows, то использовать
   Git Shell либо MinGW, итд. Будет в корне создана папка `target`, где будут образы, compose-файл и утилиты для помощи
   в инициализации базы.

```bash
./make.sh
```

2. Отправить файлы на удаленный сервер (можно использовать registry, итд) - тут указан способ с заливкой по SFTP

```bash
cd target
sftp name@vps
# папка fias должна быть создана на VPS по пути `/home/<user>/fias`, но можно использовать любую другую
cd fias
put *
exit
```

https://disk.yandex.ru/d/AKQR8DEIcVKeSw

## Api

После старта приложения по адресу: http://127.0.0.1:8080/docs будет доступен Swagger с описанием

Тест поиска: `http://127.0.0.1:8099/find/%D0%B3%20%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0,%20%D0%BF%20%D0%92%D0%BE%D1%80%D0%BE%D0%BD%D0%BE%D0%B2%D1%81%D0%BA%D0%BE%D0%B5,%20%D0%BF%20%D0%9B%D0%9C%D0%A1,%20%D1%83%D0%BB%20%D0%9D%D0%BE%D0%B2%D0%B0%D1%8F`