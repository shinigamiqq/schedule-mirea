# Schedule Mirea

Цель проекта находить неудачные и узкие места в расписании МИРЭА, и выдавать информацию о них.

# Инструкция к запуску

Установить postgresql на локальную машину.

```bash
  sudo pacman -S postgresql
  psql -U postgres
```

Создать базу данных schedule.

```bash
  CREATE database schedule;
  \c schedule

  CREATE TABLE mirea_group (
    id SERIAL PRIMARY KEY,
    group_name TEXT UNIQUE NOT NULL,
    content_length INTEGER
  );

  CREATE TABLE schedule (
    id SERIAL PRIMARY KEY,
    day TEXT,
    week_type TEXT,
    group_id INTEGER REFERENCES mirea_group(id) ON DELETE CASCADE
  );

  CREATE TABLE day (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER NOT NULL REFERENCES schedule(id) ON DELETE CASCADE,
    name TEXT,
    type TEXT,
    tutor TEXT,
    place TEXT,
    lesson_place INTEGER
  );

  CREATE TABLE alert (
    id SERIAL PRIMARY KEY,
    lesson TEXT,
    name TEXT,
    place TEXT,
    next_name TEXT,
    next_place TEXT,
    alert_type TEXT,
    group_id INTEGER REFERENCES mirea_group(id) ON DELETE CASCADE
  );
```

Установить локальный IP компьютера в домашней сети в ссылке на базу данных postgresql в файле .env

```bash
DATABASE_URL=postgresql://postgres:postgres@<IP_ADDRESS>:5432/schedule
```

Установить docker и запустить docker-compose из корневой директории проекта

```bash
  sudo pacman -S docker docker-compose
  sudo systemctl start docker
  cd schedule-mirea/
  docker-compose up --build
```

# Запуск тестов

Установить библиотеку pytest

```bash
pip install pytest
```

Установить путь python в папку с проектом

```bash
export PYTHONPATH=/your/path/to/schedule-mirea:$PYTHONPATH
```

Запустить тесты из корневой директории проекта

```bash
pytest tests/module_tests.py -v --disable-warnings
pytest tests/integration_test.py -v --disable-warnings
```

# Дополнительно

Если возникнут проблемы с тем, что docker не может подключиться к postgresql, то надо внести следующие изменения в конфиг postgresql.

```bash
sudo su
cd /var/lib/postgres/data/
vim pg_hba.conf
```

В конец файла `pg_hba.conf` добавить следующее:
```bash
host all all 192.168.0.0/24 md5
host all all <your_docker_ip> md5
```

Перезапустить postgresql
```bash
sudo systemctl restart postgresql
```
