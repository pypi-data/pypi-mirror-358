# main.py - Ядро MCP сервера

## 🎯 Назначение

Основной модуль SuperDocs, содержащий ядро MCP сервера и бизнес-логику для работы с документацией. Отвечает за создание и настройку сервера, регистрацию MCP инструментов, обработку запросов и взаимодействие с источниками документации.

## 📋 Основные компоненты

### 1. Типы данных

#### DocSource
```python
class DocSource(TypedDict):
    name: NotRequired[str]        # Имя источника (опционально)
    llms_txt: str                 # URL или путь к llms.txt файлу
    description: NotRequired[str] # Описание источника (опционально)
```

**Назначение**: Описывает источник документации с опциональными метаданными.

### 2. Утилитарные функции

#### extract_domain(url: str) -> str
```python
def extract_domain(url: str) -> str:
    """Извлекает домен из URL с протоколом и слешем"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/"
```

**Назначение**: Нормализует URL для формирования списка разрешенных доменов.

#### _is_http_or_https(url: str) -> bool
```python
def _is_http_or_https(url: str) -> bool:
    """Проверяет, является ли URL HTTP/HTTPS ссылкой"""
    return url.startswith(("http:", "https:"))
```

**Назначение**: Различает HTTP URL от локальных файлов.

#### _normalize_path(path: str) -> str
```python
def _normalize_path(path: str) -> str:
    """Нормализует file:// URL и относительные пути к абсолютным"""
    return (
        os.path.abspath(path[7:])
        if path.startswith("file://")
        else os.path.abspath(path)
    )
```

**Назначение**: Обрабатывает различные форматы путей к локальным файлам.

### 3. Основная функция создания сервера

#### create_server() -> FastMCP
```python
def create_server(
    doc_sources: list[DocSource],
    *,
    follow_redirects: bool = False,
    timeout: float = 10,
    settings: dict | None = None,
    allowed_domains: list[str] | None = None,
) -> FastMCP
```

**Параметры**:
- `doc_sources`: Список источников документации
- `follow_redirects`: Следовать ли HTTP редиректам
- `timeout`: Таймаут HTTP запросов в секундах
- `settings`: Дополнительные настройки FastMCP
- `allowed_domains`: Дополнительные разрешенные домены

**Возвращает**: Настроенный экземпляр FastMCP сервера

## 🛠️ MCP Инструменты

### 1. list_doc_sources() -> str

**Описание**: Возвращает список всех доступных источников документации.

**Логика работы**:
1. Перебирает все источники из `doc_sources`
2. Различает HTTP URL и локальные файлы
3. Формирует читаемый список с именами и путями
4. Возвращает отформатированную строку

**Пример ответа**:
```
LangGraph
URL: https://langchain-ai.github.io/langgraph/llms.txt

LocalDocs
Path: /path/to/local/docs.txt
```

### 2. fetch_docs(url: str) -> str

**Описание**: Загружает и конвертирует документ в Markdown формат.

**Логика работы для локальных файлов**:
1. Нормализует путь к файлу
2. Проверяет, что файл находится в белом списке
3. Читает содержимое файла
4. Конвертирует в Markdown через `markdownify()`
5. Возвращает результат или ошибку

**Логика работы для HTTP URL**:
1. Проверяет, что домен разрешен
2. Выполняет HTTP запрос через `httpx_client`
3. Проверяет статус ответа
4. Конвертирует HTML в Markdown
5. Возвращает результат или ошибку

**Безопасность**:
- Проверка allowed_domains для HTTP
- Проверка allowed_local_files для локальных файлов
- Обработка исключений и таймаутов
- Валидация путей

## 🔧 Архитектурные решения

### 1. Разделение источников
```python
local_sources = []
remote_sources = []

for entry in doc_sources:
    url = entry["llms_txt"]
    if _is_http_or_https(url):
        remote_sources.append(entry)
    else:
        local_sources.append(entry)
```

**Обоснование**: Разная логика обработки локальных файлов и HTTP URL.

### 2. Валидация локальных файлов
```python
for entry in local_sources:
    path = entry["llms_txt"]
    abs_path = _normalize_path(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Local file not found: {abs_path}")
```

**Обоснование**: Раннее обнаружение проблем с конфигурацией.

### 3. Система разрешений
```python
domains = set(extract_domain(entry["llms_txt"]) for entry in remote_sources)
allowed_local_files = set(_normalize_path(entry["llms_txt"]) for entry in local_sources)
```

**Обоснование**: Безопасность через белые списки.

### 4. HTTP клиент
```python
httpx_client = httpx.AsyncClient(follow_redirects=follow_redirects, timeout=timeout)
```

**Обоснование**: Один клиент для всех HTTP запросов с настраиваемыми параметрами.

## 📊 Обработка ошибок

### HTTP ошибки
```python
try:
    response = await httpx_client.get(url, timeout=timeout)
    response.raise_for_status()
    return markdownify(response.text)
except (httpx.HTTPStatusError, httpx.RequestError) as e:
    return f"Encountered an HTTP error: {str(e)}"
```

### Ошибки файловой системы
```python
try:
    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()
    return markdownify(content)
except Exception as e:
    return f"Error reading local file: {str(e)}"
```

## 🎯 Расширения и модификации

### Текущие ограничения
1. Нет кэширования результатов
2. Нет поддержки иерархической навигации
3. Простая обработка ошибок
4. Отсутствие метрик и мониторинга

### Планируемые улучшения
1. **Кэширование**: Добавление слоя кэширования для часто запрашиваемых документов
2. **Иерархическая навигация**: Новые MCP инструменты для обхода индексов
3. **Расширенная обработка ошибок**: Более детальная классификация ошибок
4. **Метрики**: Сбор статистики использования и производительности
5. **Валидация контента**: Проверка корректности llms.txt файлов

## 🔗 Зависимости

### Внешние библиотеки
- `httpx`: Асинхронный HTTP клиент
- `markdownify`: Конвертация HTML в Markdown
- `mcp.server.fastmcp`: MCP сервер фреймворк
- `typing_extensions`: Расширения типизации

### Внутренние модули
- `urllib.parse`: Парсинг URL
- `os`: Работа с файловой системой

## 📈 Производительность

### Оптимизации
- Использование `httpx.AsyncClient` для асинхронных запросов
- Переиспользование HTTP клиента
- Раннее обнаружение ошибок конфигурации

### Потенциальные узкие места
- Блокирующие операции чтения файлов
- Отсутствие кэширования
- Синхронная конвертация в Markdown

### Рекомендации по оптимизации
1. Добавить кэширование результатов
2. Использовать асинхронное чтение файлов
3. Реализовать пул соединений для HTTP запросов
4. Добавить compression для больших документов 