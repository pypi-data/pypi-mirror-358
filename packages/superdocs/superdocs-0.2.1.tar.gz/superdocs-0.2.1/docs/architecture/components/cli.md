# cli.py - Интерфейс командной строки

## 🎯 Назначение

CLI модуль SuperDocs предоставляет интерфейс командной строки для запуска и настройки MCP сервера. Обрабатывает аргументы командной строки, загружает конфигурацию из различных источников и инициализирует сервер с нужными параметрами.

## 📋 Основные компоненты

### 1. Парсер аргументов командной строки

#### CustomFormatter
```python
class CustomFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    # Сохраняет форматирование epilog и показывает значения по умолчанию
    pass
```

**Назначение**: Комбинирует два форматтера для красивого отображения help с примерами использования.

#### parse_args() -> argparse.Namespace
```python
def parse_args() -> argparse.Namespace:
    """Парсит аргументы командной строки с полной поддержкой всех опций"""
```

**Поддерживаемые аргументы**:
- `--yaml`, `-y`: Путь к YAML конфигурации
- `--json`, `-j`: Путь к JSON конфигурации  
- `--urls`, `-u`: Список URL с опциональными именами
- `--follow-redirects`: Следовать HTTP редиректам
- `--allowed-domains`: Дополнительные разрешенные домены
- `--timeout`: Таймаут HTTP запросов
- `--transport`: Протокол транспорта (stdio/sse)
- `--log-level`: Уровень логирования для SSE
- `--host`: Хост для SSE сервера
- `--port`: Порт для SSE сервера
- `--version`, `-V`: Показать версию

### 2. Загрузка конфигурации

#### load_config_file()
```python
def load_config_file(file_path: str, file_format: str) -> List[Dict[str, str]]:
    """Загружает конфигурацию из YAML или JSON файла"""
```

**Особенности**:
- Поддержка YAML и JSON форматов
- Валидация структуры конфигурации
- Обработка ошибок парсинга
- Завершение программы при ошибках

### 3. Обработка URL

#### create_doc_sources_from_urls()
```python
def create_doc_sources_from_urls(urls: List[str]) -> List[DocSource]:
    """Создает источники документации из списка URL с опциональными именами"""
```

**Поддерживаемые форматы**:
- `"url"` - простой URL без имени
- `"name:url"` - URL с именем (кроме http/https)

## 🔧 Архитектура CLI

### 1. Жизненный цикл запуска

```mermaid
graph TD
    A[main()] --> B{Есть аргументы?}
    B -->|Нет| C[Показать help]
    B -->|Да| D[parse_args()]
    D --> E{Источники указаны?}
    E -->|Нет| F[Ошибка: нужны источники]
    E -->|Да| G[Загрузка источников]
    G --> H[Создание сервера]
    H --> I{Transport = SSE?}
    I -->|Да| J[Показать splash]
    I -->|Нет| K[Запуск сервера]
    J --> K
```

### 2. Обработка конфигурации

```python
# Объединение источников из разных методов
doc_sources: List[DocSource] = []

if args.yaml:
    doc_sources.extend(load_config_file(args.yaml, "yaml"))
if args.json:
    doc_sources.extend(load_config_file(args.json, "json"))
if args.urls:
    doc_sources.extend(create_doc_sources_from_urls(args.urls))
```

**Принцип**: Все источники объединяются, позволяя комбинировать разные методы конфигурации.

### 3. Настройка транспорта

```python
settings = {
    "host": args.host,
    "port": args.port,
    "log_level": "INFO",
}

server = create_server(
    doc_sources,
    follow_redirects=args.follow_redirects,
    timeout=args.timeout,
    settings=settings,
    allowed_domains=args.allowed_domains,
)

server.run(transport=args.transport)
```

## 📊 Форматы конфигурации

### YAML конфигурация
```yaml
# sample_config.yaml
- name: LangGraph Python
  llms_txt: https://langchain-ai.github.io/langgraph/llms.txt
  description: LangGraph documentation

- name: Local Docs
  llms_txt: /path/to/local/docs.txt
```

### JSON конфигурация
```json
[
  {
    "name": "LangGraph Python",
    "llms_txt": "https://langchain-ai.github.io/langgraph/llms.txt",
    "description": "LangGraph documentation"
  }
]
```

### URL аргументы
```bash
# Простые URL
superdocs --urls "https://example.com/llms.txt"

# URL с именами  
superdocs --urls "LangGraph:https://example.com/llms.txt" "LocalDocs:/path/to/file.txt"
```

## 🎨 Пользовательский интерфейс

### Help сообщение
```
MCP LLMS-TXT Documentation Server

Examples:
  # Directly specifying llms.txt URLs with optional names
  mcpdoc --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt
  
  # Using a local file (absolute or relative path)
  mcpdoc --urls LocalDocs:/path/to/llms.txt --allowed-domains '*'
  
  # Using a YAML config file
  mcpdoc --yaml sample_config.yaml
```

### Splash экран (SSE режим)
```
    ███╗   ███╗ ██████╗██████╗ ██████╗  ██████╗  ██████╗
    ████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔════╝
    ██╔████╔██║██║     ██████╔╝██║  ██║██║   ██║██║
    ██║╚██╔╝██║██║     ██╔═══╝ ██║  ██║██║   ██║██║
    ██║ ╚═╝ ██║╚██████╗██║     ██████╔╝╚██████╔╝╚██████╗
    ╚═╝     ╚═╝ ╚═════╝╚═╝     ╚═════╝  ╚═════╝  ╚═════╝

Launching MCPDOC server with 2 doc sources
```

## 🔐 Валидация и безопасность

### Проверка входных данных
```python
# Проверка наличия источников
if not (args.yaml or args.json or args.urls):
    print("Error: At least one source option (--yaml, --json, or --urls) is required")
    sys.exit(1)
```

### Обработка ошибок загрузки
```python
try:
    with open(file_path, "r", encoding="utf-8") as file:
        # Загрузка конфигурации
except (FileNotFoundError, yaml.YAMLError, json.JSONDecodeError) as e:
    print(f"Error loading config file: {e}", file=sys.stderr)
    sys.exit(1)
```

## 🚀 Транспортные протоколы

### STDIO Transport
- **Назначение**: Интеграция с IDE (Cursor, Windsurf, Claude Desktop)
- **Характеристики**: Бесшумный запуск, обмен через stdin/stdout
- **Использование**: Основной режим для AI-ассистентов

### SSE Transport  
- **Назначение**: Веб-интерфейс и отладка
- **Характеристики**: HTTP сервер, splash экран, логирование
- **Настройки**: Хост, порт, уровень логирования

## 📈 Расширения и улучшения

### Текущие возможности
1. **Гибкая конфигурация**: Поддержка YAML, JSON, CLI аргументов
2. **Комбинирование источников**: Можно миксовать разные методы
3. **Два транспорта**: STDIO для IDE, SSE для веб
4. **Валидация**: Проверка аргументов и конфигурации
5. **Справочная система**: Детальная help информация

### Потенциальные улучшения
1. **Интерактивный режим**: Пошаговая настройка конфигурации
2. **Auto-discovery**: Автоматическое обнаружение llms.txt файлов
3. **Конфигурационные профили**: Сохранение часто используемых настроек
4. **Валидация источников**: Проверка доступности источников при запуске
5. **Расширенное логирование**: Более детальные логи для отладки

### Планируемые CLI опции
```bash
# Новые опции для browse_index функциональности
superdocs --urls "N8N:https://example.com/index" \
         --max-hierarchy-depth 3 \
         --enable-caching \
         --cache-ttl 3600 \
         --index-patterns "**/index" "**/*_index_*"
```

## 🔗 Интеграция с основным сервером

### Передача параметров
```python
server = create_server(
    doc_sources,                    # Источники документации
    follow_redirects=args.follow_redirects,  # HTTP настройки
    timeout=args.timeout,
    settings=settings,              # Настройки транспорта
    allowed_domains=args.allowed_domains,    # Безопасность
)
```

### Версионирование
```python
from superdocs._version import __version__

parser.add_argument(
    "--version", "-V",
    action="version",
    version=f"mcpdoc {__version__}",
)
```

## 🧪 Тестирование CLI

### Тестовые сценарии
1. **Запуск без аргументов**: Должен показать help
2. **Неверная конфигурация**: Должен завершиться с ошибкой
3. **Комбинирование источников**: Все источники должны загружаться
4. **Валидация аргументов**: Проверка корректности параметров
5. **Различные транспорты**: STDIO и SSE режимы

### Примеры тестовых команд
```bash
# Базовый тест
superdocs --urls "Test:https://example.com/llms.txt"

# Тест с конфигурацией
superdocs --yaml sample_config.yaml --transport sse --port 9000

# Тест с локальными файлами
superdocs --urls "Local:/path/to/file.txt" --allowed-domains "*"
``` 