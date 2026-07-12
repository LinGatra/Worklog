# План тестирования

Порядок — bottom-up: от модели к endpoint-тестам, каждый следующий слой опирается на уже проверенный предыдущий. Контракт поведения — в `Requirements.md`, здесь только чек-лист выполнения.

## Сессия 1 — Модели / БД-констрейнты (интеграционные, реальный Postgres)
- [ ] Создание `Client`/`Offering`/`AltPrice`/`History` с валидными данными — happy path
- [ ] `UniqueConstraintViolation`: повтор `client_name`
- [ ] `UniqueConstraintViolation`: повтор `offering_name`
- [ ] `UniqueConstraintViolation`: повтор пары `(client_id, offering_id)` в `AltPrice`
- [ ] `ForeignKeyViolation`: `AltPrice` с несуществующим `client_id`/`offering_id`
- [ ] `ForeignKeyViolation`: `History` с несуществующим `client_id`/`offering_id`
- [ ] `NullConstraintViolation`: явный `null` на `NOT NULL` поле при прямой записи через репозиторий
- [ ] Check-constraint: отрицательная `offering_price`/`alt_price` при прямой записи через репозиторий (в обход Pydantic)

## Сессия 2 — BaseRepository (интеграционные)
- [ ] `create`: happy path
- [ ] `create`: `23505` → `UniqueConstraintViolation`
- [ ] `create`: `23503` → `ForeignKeyViolation`
- [ ] `create`: `23502` → `NullConstraintViolation`
- [ ] `update`: happy path
- [ ] `update`: `23503` → `ForeignKeyViolation`
- [ ] `update`: `23505` → `UniqueConstraintViolation`
- [ ] `update`: `23502` → `NullConstraintViolation`
- [ ] `remove`: happy path
- [ ] `remove`: удаление сущности с зависимой строкой → `ForeignKeyViolation`
- [ ] `get`/`get_by_id`: найдено / `NotFound` при отсутствии
- [ ] `get_multi`: пустая коллекция, пагинация `skip`/`limit`, дефолтные значения

## Сессия 3 — HistoryRepository (интеграционные, отдельный контракт от BaseRepository)
- [ ] `create`: цена берётся из `AltPrice`, если она есть для пары client/offering
- [ ] `create`: цена берётся из `Offering.offering_price`, если альт-цены нет (проверка `coalesce`)
- [ ] `create`: несуществующий `client_id` → `ForeignKeyViolation`
- [ ] `create`: несуществующий `offering_id` → `NotFound` (зафиксировать асимметрию с `client_id` явным тестом)

## Сессия 4 — Exception handlers
- [ ] `NotFound` → 404, тело `{"error": {"code": 404, ...}}`
- [ ] `ForeignKeyViolation` → 400
- [ ] `UniqueConstraintViolation` → 409
- [ ] `NullConstraintViolation` → 400

## Сессия 5 — BaseService (юнит, репозиторий замокан)
- [X] `create`/`get_by_id`/`get_all`/`update`/`delete`: доменное исключение из замоканного репозитория пробрасывается без изменений (не HTTP-исключение)
- [X] Успешные вызовы: ровно одно `business_event_succeeded` с правильными `model`/`action`
- [X] Неуспешные вызовы: ровно одно `business_event_failed`, `error_type` = имя реального доменного исключения
- [X] `update`: ровно один вызов логгера на весь метод (не два)

## Сессия 6 — HistoryService (юнит)
- [ ] `get_by_id`/`get_all`: аналогично BaseService
- [ ] `create`: `business_event_succeeded`/`business_event_failed` логируются так же, как у остальных `create`

## Сессия 7 — middleware
- [ ] `request_id` присутствует в ответе и в каждой строке лога запроса
- [ ] Контролируемые доменные исключения (400/404/409): только `request_finished` с нужным `status_code`, без `request_failed`
- [ ] Настоящий необработанный 500: `request_failed` присутствует

## Сессия 8 — Endpoint-тесты (httpx AsyncClient + ASGITransport, testcontainers)
- [ ] Полный CRUD-цикл по каждому роутеру: 200/201, 404, тело ошибки `{"error": {"code", "message"}}`
- [ ] 422 от Pydantic при некорректном типе/отсутствующем обязательном поле
- [ ] 422 при пустой строке в `client_name`/`offering_name`
- [ ] PATCH с явным JSON `null` на `NOT NULL`-по-модели поле → 400
- [ ] FK/Unique/Null-violation через полный CRUD-цикл — конечный HTTP-статус и структура ответа
- [ ] Логи `request_finished` без `request_failed` для контролируемых исключений — на уровне полного запроса, не только middleware-юнита
