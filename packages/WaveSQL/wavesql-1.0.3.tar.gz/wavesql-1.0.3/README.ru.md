# 🌊 WaveSQL

[`Читайте эту страницу на английском`](https://github.com/WaveTeamDevs/WaveSQL/blob/main/README.md)

**WaveSQL** — лёгкая, но мощная Python-библиотека для безопасной, синхронной и асинхронной работы с MySQL и MariaDB.

> Разработано [`WaveTeam`](https://github.com/WaveTeamDevs) под руководством [`eelus1ve`](https://github.com/eelus1ve)

---

## 🚀 Возможности

- 🔌 Простое подключение к базе данных через config.ini или словарь
- ⚙️ Автоматическая инициализация структуры БД при первом запуске
- 🧠 Поддержка вызова хранимых процедур (CALL)
- 🪝 Защищённые методы (через @protected) — предотвращают прямой вызов критичных функций
- 🐍 Асинхронная версия с аналогичным API
- 🪵 Встроенное логирование в базу данных + цветной вывод в консоль (colorama)
- 🧠 Автоматическая генерация Python-кода (Python Bridge) из SQL-файла
- 🧩 Гибкая конфигурация: dictionary=True, цветной вывод, pprint, контроль backtrace
- 🛡️ Отлавливание и логирование ошибок с трассировкой (traceback)
- 🧪 Защита от неполных или отсутствующих SQL-файлов

---

## 📦 Установка

```bash
pip install wavesql
```

## 🧰 Использование

🔹 Простой пример
```python
from wavesql.sync import WaveSQL

db = WaveSQL(
    is_dictionary=True,
    is_console_log=True,
    is_log_backtrace=True,
    is_auto_start=True
)

db.log(level=3, text="All is good!")

```

---


## 🌀 Асинхронная версия

```python
from wavesql.aio import AsyncWaveSQL

adb = AsyncWaveSQL(
    is_dictionary=True,
    is_console_log=True,
    is_log_backtrace=True,
    is_auto_start=True
)

await adb.log(level=3, text="Async logging works!")
```

# Все методы и поведение идентичны синхронной версии
# Просто используйте await, и импортируйте из wavesql.aio AsyncWaveSQL

---


## 🧠 Генерация Python-кода из SQL


Если в вашей SQL-директории присутствует файл `queries.sql`, WaveSQL может автоматически сгенерировать Python-код для вызова SQL-запросов, описанных в этом файле. 

Пример содержимого `queries.sql`:

```sql
create get_user with query SELECT * FROM users WHERE id = {% extend user_id : int %} LIMIT 1;
```

Пояснение к синтаксису:
- `create get_user` — объявляет имя функции/метода, который будет сгенерирован.

- `with query` — ключевое слово, после которого указывается SQL-запрос.

- Внутри запроса конструкция `{% extend user_id : int %}` означает, что в сгенерированном методе будет параметр `user_id` типа `int`.

- В SQL-запросе вместо этого параметра будет использоваться безопасная подстановка значения (`%s` или аналог), чтобы избежать SQL-инъекций.


Просто установите флаг `is_create_python_bridge=True` при инициализации:

```python

db = WaveSQL(
    is_create_python_bridge=True,
    ...
)

```

В результате будут созданы файлы:

- `database.py` – синхронный интерфейс

- `asyncdatabase.py` – асинхронный интерфейс

- `aio.py` – точка входа для асинхронного API

- `__init__.py` – точка входа для синхронного API

- библиотечные SQL-файлы, которые инициализируют базу данных и создают необходимые минимальные таблицы для корректной работы модуля

---


## 🧰 Использование c is_create_python_bridge=True

📁 Структура проекта (До запуска `run.py`)
```bash
database/
├── sql/
│   ├── 2_init_users.sql
│   └── queries.sql
├── run.py
```

🐍 Файл run.py
```python
from wavesql.sync import WaveSQL

db = WaveSQL(
    config="path_to_my_settings.ini", path_to_sql="database/sql", is_console_log=True,
    is_log_backtrace=True, is_auto_start=True, is_create_python_bridge=True
)
```

Файлы с именами, содержащими `_init_` и числовой префикс (например, `0_init_users.sql`), инициализируются в базу данных в порядке возрастания этого числа.  
При этом префикс должен быть целым неотрицательным числом — отрицательные значения зарезервированы библиотекой.  

Файл `queries.sql` используется для автоматической генирации методов-запросов которые создают два моста (синхронный и асинхронный)  

Пример `queries.sql`:
```sql
create get_user with query SELECT * FROM users WHERE id = {% extend user_id : int %} LIMIT 1;
```

Вывод:
```python
# database.py
def get_user(self, user_id: int) -> dict | None:
    return self._db_query("SELECT * FROM users WHERE id = %s LIMIT 1", (user_id, ), fetch=1)

# asyncdatabase.py
async def get_user(self, user_id: int) -> dict | None:
    return await self._db_query("SELECT * FROM users WHERE id = %s LIMIT 1", (user_id, ), fetch=1)
```

📁 Структура проекта (После запуска `run.py`)
```bash
database/
├── sql/
│   ├── 0_init_db.sql
│   ├── 1_init_logs.sql
│   ├── 2_init_users.sql
│   └── queries.sql
├── sync.py
├── aio.py
├── asyncdatabase.py
├── database.py
├── run.py
```

---


## 🧾 Требования

- Python 3.12.10+
- mysql-connector-python=9.3.0
- colorama=0.4.6

---

## 📁 Структура проекта
```bash
WaveSQL/
├── wavesql/
│   ├── sync.py
│   ├── aio.py
│   ├── sqlFileObject.py
│   ├── constants.py
│   ├── asyncdatabase.py
│   ├── database.py
│   ├── errors.py
│   ├── config.ini
│   ├── sql/
│   │   ├── 0_init_db.sql
│   │   └── 1_init_logs.sql
│   ├── python/
│   │   ├── sync.py
│   │   ├── aio.py
│   │   ├── asyncdatabase.py
│   │   └── database.py
├── README.md
├── NOTICE
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

---

## 📜 Журнал изменений

См. [`CHANGELOG.ru.md`](https://github.com/WaveTeamDevs/WaveSQL/blob/main/CHANGELOG.ru.md) для подробной истории версий.

---

## 🔮 Планируемые функции / Дорожная карта

- [ ] Поддержка SQLite
- [ ] Автоматическая проверка синтаксиса SQL кода 
- [ ] Автоматическая подстановка типов данных из SQL-таблиц в Python-код
- [ ] Распознавание выходных данных процедур
- [ ] Поддержка PostgreSQL
- [ ] Генерация API для других языков

---


## 👤 Автор
- Darov Alexander (eelus1ve)
- Email: darov-alexander@outlook.com
- GitHub: [`@eelus1ve`](https://github.com/eelus1ve)
- Разработано в рамках [`WaveTeam`](https://github.com/WaveTeamDevs)

---

## 🔗 Ссылки
- 🌍 Репозиторий: [`github.com/WaveTeamDevs/WaveSQL`](https://github.com/WaveTeamDevs/WaveSQL)
- 🧠 Организация: [`WaveTeamDevs`](https://github.com/WaveTeamDevs)

---
