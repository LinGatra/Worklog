## Памятка по функционалу

1. Роутеры:
   1. Получают HTTP запрос
   2. Вызывают сервис
   3. Возвращают ответ от сервиса обратно в HTTP
2. Схемы:
   1. Валидируют данные на вход
   2. Приводят по необходимости и возможности к правильным типам
3. Модели:
   1. Описывают структуру сущностей в базе данных
4. Сервисы:
   1. Вызывают репозиторий
   2. Логируют бизнес события
   3. Возвращают данные в роутеры (или пробрасывают доменное исключение без изменений — HTTP-перевод сервис больше не делает, см. ниже)
5. Репозитории:
   1. Обращаются в базу данных
   2. Превращают ошибки (статус коды SQL) и пустые результаты, требующие явной обработки, в доменные исключения
   3. Отдают данные в сервисы
6. middleware:
   1. Создаёт request_id
   2. Записывает состояния данных на каждом этапе, привязывая их (состояния) к request_id
   3. Не логирует `request_failed` для доменных исключений, у которых есть зарегистрированный exception handler (см. ниже) — это штатный, а не аварийный исход запроса
7. Exception handlers (новый слой, появился при закрытии Q4):
   1. Единственное место, где доменное исключение превращается в HTTP-ответ
   2. Регистрируются в `main.py` через `app.add_exception_handler`
   3. Формат тела ошибки единый: `{"error": {"code", "message"}}`

---

## Контракт: доменные исключения → HTTP (актуальная схема)

Начиная с закрытия Q4, перевод доменных исключений в HTTP происходит **не в сервисе**, а в FastAPI exception handlers на границе приложения. Сервис доменные исключения не ловит и не оборачивает — пробрасывает как есть.

| Доменное исключение          | SQLSTATE / условие                                  | Кто бросает                                                                                     | Кто переводит в HTTP        | Код |
| ----------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------- | --- |
| `NotFound`                    | пустой результат `get`/`get_multi`/пустой `SELECT`   | `BaseRepository.get`, `HistoryRepository.get`, `HistoryRepository.create` (при пустом `offering_id`, было Q7) | exception handler в `main.py` | 404 |
| `UniqueConstraintViolation`   | `23505`                                              | `BaseRepository.create`, `BaseRepository.update`                                                 | exception handler в `main.py` | 409 |
| `ForeignKeyViolation`         | `23503`                                              | `BaseRepository.create`, `BaseRepository.update`, `BaseRepository.remove`, `HistoryRepository.create` | exception handler в `main.py` | 400 |
| `NullConstraintViolation`     | `23502` (введено при закрытии Q9)                    | `BaseRepository.create`, `BaseRepository.update`                                                 | exception handler в `main.py` | 400 |

Это все доменные исключения в системе (`app/exception_handling/domain_exceptions.py`). Всё остальное (например, `23514` check-constraint — потенциальный Q10) по-прежнему нигде не перехватывается и падает как raw 500.

---

## Закрытые вопросы (Q1–Q9)

Коротко — что было и как решено. Оставлено для истории, чтобы при написании тестов не приходилось восстанавливать контекст заново.

- **Q1.** `BaseRepository.update` не ловил `UniqueConstraintViolation` — добавлена ветка `23505` по аналогии с `create`.
- **Q2.** `BaseRepository.remove` не ловил `IntegrityError` вообще — добавлен `try/except` с веткой `23503`.
- **Q3.** `BaseService.get_all` ловил `NotFound`, которого `get_multi` не бросает — мёртвая ветка убрана вместе со всем `try/except` при переходе на вариант Б (сервис ничего не ловит).
- **Q4.** Декоратор `log_business_event` ловил доменные исключения, которые до него не долетали (сервис уже успевал перевести их в HTTP). Решено архитектурно: убрали перевод в HTTP из `BaseService`/`HistoryService`, добавили exception handlers в `main.py`. Теперь `except NotFound / ForeignKeyViolation / UniqueConstraintViolation / NullConstraintViolation` в декораторе реально достижимы, `error_type` в логе — точное имя доменного исключения. Подтверждено логами: `WARNING business_event_failed error_type=NotFound` + `request_finished status_code=404`, без `request_failed`.
- **Q5.** `BaseService.update` вызывал залогированный `get_by_id`, из-за чего один PATCH давал два бизнес-события. Решено попутно с рефакторингом Q4: `update` теперь берёт объект напрямую через `self.repo.get(...)`, минуя логируемую обёртку. Подтверждено логами: один PATCH = 4 записи (open/close HTTP + ровно 2 бизнес-события: `get_by_id`-логика больше не задействуется отдельно).
- **Q6.** `HistoryService.create` был единственным `create` без бизнес-лога — добавлен `@log_business_event(action='create')`.
- **Q7.** `HistoryRepository.create` с несуществующим `offering_id` давал `SELECT` с пустым результатом → `INSERT ... FROM SELECT` вставлял 0 строк → `result.scalar_one()` бросал необработанный `NoResultFound`. Решено: при пустом результате `select_stmt` явно бросается `NotFound` до попытки `scalar_one()` — тем самым `offering_id` и `client_id` теперь дают одинаковый по духу результат (404/400 вместо асимметрии 500/400, которая была раньше).
- **Q8.** Отсутствовал `min_length` на `client_name`/`offering_name`, пустая строка проходила валидацию. Добавлен `min_length=1` в обеих схемах.
- **Q9.** Explicit `null` в PATCH-схемах (`{"offering_name": null}`) не отфильтровывался `exclude_unset=True` (он вырезает только *отсутствующие* поля, не явный `null`) и долетал до `NOT NULL` колонки → `23502` → необработанный 500. Решено по аналогии с остальными SQLSTATE: добавлено доменное исключение `NullConstraintViolation`, `BaseRepository.create/update` ловят `23502` и бросают его, exception handler переводит в 400. Проверено на реальном запросе (важно: JSON требует `null`, не Python-`None` — с `None` в теле запроса падает ещё раньше, на этапе разбора JSON, это отдельная и ожидаемая ошибка `json_invalid`, не относится к Q9).

Открытых вопросов из исходного списка не осталось. Потенциальный кандидат на будущее — check-constraint `23514` (`offering_price >= 0` / `alt_price >= 0`), условно назван Q10, но пока не заведён как задача: через API недостижим, раз в схемах уже стоит `ge=0`.

---

## Что необходимо проверять (по слоям)

### Роутеры
- Логики нет — отдельно не тестируем. Проверяется только на уровне endpoint-тестов (httpx), что роутер правильно прокидывает статус/тело от сервиса, включая ошибочные ответы через exception handlers.

### Схемы
1. Данные валидируются корректно (типы, границы: `ge=0` для цен, `min_length=1, max_length=100` для строк)
2. Крайние случаи: пустая строка (закрыто, Q8), `null` в Update-схемах (закрыто на уровне обработки, Q9 — но сама схема explicit-null по-прежнему пропускает, это осознанно, страховка на уровне БД/репозитория)
3. Не противоречат ограничениям **Моделей**

### Модели
1. Корректно связаны между собой (FK `AltPrice.client_id → Client`, `AltPrice.offering_id → Offering`, `History.client_id/offering_id`)
2. `CheckConstraint`: `offering_price >= 0`, `alt_price >= 0` — нарушение даёт `IntegrityError` (`23514`), которая нигде не перехватывается (потенциальный Q10, отдельный тест на уровне репозитория/модели в обход Pydantic)
3. `UniqueConstraint('client_id', 'offering_id')` на `AltPrice` — крайний случай: повторная альт-цена для той же пары клиент/оффер

### Сервисы
1. Ничего не ловят и не переводят в HTTP — доменное исключение, брошенное репозиторием, должно долететь наружу из сервиса **без изменений** (это теперь явный контракт, стоит зафиксировать тестом-инвариантом на каждый метод)
2. Корректно логируют события — `error_type` в логе должен совпадать с именем реального доменного исключения; количество вызовов логгера на один HTTP-запрос — ровно по числу бизнес-действий (для PATCH — одно, не два, см. закрытый Q5)
3. Корректно работают с сессиями и транзакциями ORM: `session.begin()` должен быть **первым** обращением к сессии в методе (иначе autobegin конфликтует с явным `begin()` — это и была причина `InvalidRequestError` на PATCH); там, где сервису нужен объект перед изменением (`update`), fetch должен происходить внутри того же `async with session.begin()`, а не до него

### Репозитории
1. Правильно выполняют логику действий с данными (в т.ч. специфичный `HistoryRepository.create` — INSERT FROM SELECT с ценой из `AltPrice` с фоллбеком на `Offering.offering_price`)
2. Корректно ловят и превращают в доменные исключения все относящиеся к бизнес-логике SQLSTATE (`23503`, `23505`, `23502`) и пустые результаты, требующие явной обработки (`NotFound` вместо `NoResultFound`)
3. Не создают лишних запросов в базу (N+1 не актуален пока — простые модели без relationship-загрузок)

### Exception handlers (новый слой)
1. Для каждого доменного исключения — свой handler, свой статус, единый формат тела `{"error": {"code", "message"}}`
2. Тест на каждую пару (доменное исключение → статус): `NotFound`→404, `ForeignKeyViolation`→400, `UniqueConstraintViolation`→409, `NullConstraintViolation`→400
3. Косвенно проверяется, что порядок регистрации `add_exception_handler` в `main.py` не важен (исключения не пересекаются по типам)

### middleware
1. Создаёт `request_id`
2. Правильно записывает события в логи: нужные поля, в нужном формате
3. Для запросов, завершившихся контролируемым доменным исключением (404/400/409), в логе должен быть только `request_finished` с соответствующим `status_code` — **без** `request_failed`. Для по-настоящему необработанных исключений (raw 500) — наоборот, должен появиться `request_failed`. Оба случая стоит покрыть тестом, это наблюдаемое поведение, подтверждённое вручную, но не зафиксированное автотестом

---

## Матрица тестовых сценариев

Легенда: **[OK]** — контракт понятен, можно тестировать как есть.

### Модели / БД-констрейнты (интеграционные, реальный Postgres)
- [OK] Создание `Client`/`Offering`/`AltPrice`/`History` с валидными данными
- [OK] `UniqueConstraintViolation`: повтор `client_name`, повтор `offering_name`, повтор пары `(client_id, offering_id)` в `AltPrice`
- [OK] `ForeignKeyViolation`: `AltPrice`/`History` с несуществующим `client_id`/`offering_id`
- [OK] `NullConstraintViolation`: explicit `null` на `NOT NULL` поле при прямой записи через репозиторий
- [OK] Check-constraint: отрицательная `offering_price`/`alt_price` при прямой записи через репозиторий (в обход Pydantic) — подтверждает защиту на двух уровнях; HTTP-статус не проверяем (недостижимо через API), только факт `IntegrityError`

### BaseRepository (интеграционные)
- [OK] `create`: happy path; `23505` → `UniqueConstraintViolation`; `23503` → `ForeignKeyViolation`; `23502` → `NullConstraintViolation`
- [OK] `update`: happy path; `23503` → `ForeignKeyViolation`; `23505` → `UniqueConstraintViolation`; `23502` → `NullConstraintViolation`
- [OK] `remove`: happy path; удаление сущности с зависимой строкой → `ForeignKeyViolation`
- [OK] `get`/`get_by_id`: найдено / `NotFound` при отсутствии
- [OK] `get_multi`: пустая коллекция, пагинация `skip`/`limit`, дефолтные значения

### HistoryRepository (интеграционные, отдельно от BaseRepository — другой контракт)
- [OK] `create`: цена берётся из `AltPrice`, если она есть для пары client/offering
- [OK] `create`: цена берётся из `Offering.offering_price`, если альт-цены нет (проверка `coalesce`)
- [OK] `create`: несуществующий `client_id` → `ForeignKeyViolation`
- [OK] `create`: несуществующий `offering_id` → `NotFound` (было Q7, симметрично `client_id` по HTTP-коду смысла — но само доменное исключение разное: `NotFound` vs `ForeignKeyViolation`, это стоит явно зафиксировать тестом, чтобы не расползлось незаметно)

### BaseService (юнит, репозиторий замокан)
- [OK] Каждый метод (`create`/`get_by_id`/`get_all`/`update`/`delete`): доменное исключение из замоканного репозитория пробрасывается из сервиса **без изменений** (не HTTP-исключение)
- [OK] Успешные вызовы: ровно одно `business_event_succeeded` с правильным `model`/`action`
- [OK] Неуспешные вызовы: ровно одно `business_event_failed` с `error_type`, равным имени реального доменного исключения
- [OK] `update`: ровно один вызов логгера на весь метод (не два, как было при Q5), объект достаётся внутри одной транзакции с изменением

### HistoryService (юнит)
- [OK] `get_by_id`/`get_all`: аналогично BaseService
- [OK] `create`: теперь тоже логируется (закрыт Q6) — проверить наличие `business_event_succeeded`/`business_event_failed` по тем же правилам, что и у остальных `create`

### Exception handlers (юнит или лёгкие integration)
- [OK] `NotFound` → 404, тело `{"error": {"code": 404, ...}}`
- [OK] `ForeignKeyViolation` → 400
- [OK] `UniqueConstraintViolation` → 409
- [OK] `NullConstraintViolation` → 400

### Endpoint-тесты (httpx AsyncClient + ASGITransport, реальный Postgres через testcontainers)
- [OK] Полный CRUD-цикл по каждому роутеру: 200/201, 404, тело ошибки в формате `{"error": {"code", "message"}}`
- [OK] 422 от Pydantic при некорректном типе/отсутствующем обязательном поле
- [OK] 422 при пустой строке в `client_name`/`offering_name` (закрыт Q8)
- [OK] PATCH с явным `null` (JSON `null`, не Python `None`!) на nullable-по-схеме/`NOT NULL`-по-модели поле → 400 (закрыт Q9)
- [OK] FK/Unique/Null-violation через полный CRUD-цикл — конечный HTTP-статус и структура ответа
- [OK] `request_id` присутствует в ответе/логах на каждый запрос (middleware)
- [OK] Логи `request_finished` без `request_failed` для контролируемых доменных исключений (400/404/409); `request_failed` только для реально необработанных 500

---

## Предлагаемый порядок дальнейшей работы

1. Bottom-up: модели/констрейнты → `BaseRepository` (+ отдельно `HistoryRepository`) → exception handlers → `BaseService` (+ отдельно `HistoryService`) → middleware → endpoint-тесты поверх уже проверенных слоёв.
2. Endpoint-тесты писать в последнюю очередь и по минимуму: раз у роутеров нет логики, их задача — подтвердить, что слои действительно собраны вместе правильно (статусы, формат ошибки, request_id, поведение логов), а не переповторять всё, что уже проверено ниже.
3. При появлении новых доменных исключений в будущем — не забывать регистрировать соответствующий exception handler в `main.py`; иначе исключение долетит до `LoggingMiddleware` как необработанное и даст raw 500 вместо контролируемого ответа.
