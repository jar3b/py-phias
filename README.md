# py-fias
WSGI application they can serve FIAS (Russian Address Object DB)

Простое приложение для работы с БД ФИАС, написано для Python 2.7

## Установка
Протестирована работа на следующих ОС: Windows (8.1) и Debian Jessie

### Зависимости

Для работы приложения необходимо достаточное кол-во RAM (1Gb+) и 4.5Gb места на диске 
(3-3.5Gb для скачивания архива с базой и  300-400Mb для индексов Sphinx). Также необходимы root права 
(или Администратора, для OS Windows), для работы демона Sphinx и предварительной установки. 

Предварительно нужно установить и настроить:

1. Python 2.7 [Windows](https://www.python.org/downloads/windows/), [Debian](https://www.python.org/downloads/source/) 
(`sudo apt-get install python2.7 python2.7-dev`), pip

2. PostgreSql 9.5 и выше (из-за _ON CONFLICT_)

3. Sphinx 2.2.3 и новее (из-за синтаксиса _MAYBE_)

### Windows
1. Установить sphinxapi последней версии: 

`python -m pip install https://github.com/Romamo/sphinxapi/zipball/master`
    