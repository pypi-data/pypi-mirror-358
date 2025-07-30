# pyproject.toml - Конфигурация проекта

## 🎯 Назначение

Основной конфигурационный файл SuperDocs, определяющий метаданные проекта, зависимости, настройки сборки и инструменты разработки. Следует стандарту PEP 518 для современных Python проектов.

## 📋 Структура конфигурации

### Метаданные проекта
```toml
[project]
name = "superdocs"
version = "0.1.2"
description = "Enhanced MCP server for documentation with superpowers"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
```

**Ключевые характеристики**:
- **Имя**: `superdocs` (публикуется в PyPI)
- **Версия**: Синхронизируется с `_version.py`
- **Python**: Требует Python 3.10+ для современных возможностей
- **Лицензия**: MIT для максимальной совместимости

### Точки входа
```toml
[project.scripts]
superdocs = "superdocs.cli:main"
```

**Назначение**: Регистрирует консольную команду `superdocs` для запуска приложения.

## 🔧 Управление зависимостями

### Основные зависимости
```toml
dependencies = [
    "httpx>=0.28.1",        # Асинхронный HTTP клиент
    "markdownify>=1.1.0",   # Конвертация HTML в Markdown
    "mcp[cli]>=1.4.1",      # MCP фреймворк с CLI поддержкой
    "pyyaml>=6.0.1",        # YAML парсинг для конфигурации
]
```

#### Обоснование выбора версий
- **httpx**: Современный асинхронный HTTP клиент, замена requests
- **markdownify**: Надежная конвертация HTML в Markdown
- **mcp[cli]**: Включает дополнительные CLI утилиты
- **pyyaml**: Стандартная библиотека для YAML

### Дополнительные зависимости
```toml
[project.optional-dependencies]
test = [
    "pytest>=8.3.4",           # Современный тестовый фреймворк
    "pytest-asyncio>=0.25.3",  # Поддержка async тестов
    "pytest-cov>=6.0.0",       # Покрытие кода
    "pytest-mock>=3.14.0",     # Мокирование
    "pytest-socket>=0.7.0",    # Контроль сетевых запросов
    "pytest-timeout>=2.3.1",   # Таймауты для тестов
    "ruff>=0.9.7",              # Линтер и форматтер
]
```

#### Философия тестирования
- **pytest**: Современный подход к тестированию
- **async support**: Тестирование асинхронного кода
- **coverage**: Контроль качества тестов
- **mocking**: Изоляция внешних зависимостей
- **network control**: Предотвращение случайных сетевых запросов

## 🏗️ Система сборки

### Настройка Hatchling
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Преимущества Hatchling**:
- Современный и быстрый сборщик
- Хорошая интеграция с pyproject.toml
- Поддержка различных форматов пакетов
- Минимальные зависимости

### Альтернативы
```toml
# Альтернативные системы сборки:

# Poetry
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

# Setuptools
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

## 🧪 Конфигурация тестирования

### Настройки pytest
```toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q -v --durations=5"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

#### Детализация опций
- **-ra**: Отчет о всех результатах тестов
- **-q**: Тихий режим для чистого вывода
- **-v**: Подробные имена тестов
- **--durations=5**: Показать 5 самых медленных тестов
- **asyncio_mode="auto"**: Автоматическая поддержка async

### Путь тестов
```toml
testpaths = ["tests"]
```
Определяет директории для поиска тестов.

## 🎨 Инструменты разработки

### Потенциальные конфигурации

#### Ruff (линтер/форматтер)
```toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Длинные строки

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

#### Black (форматтер)
```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'
```

#### MyPy (типизация)
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## 📦 Конфигурация публикации

### Метаданные для PyPI
```toml
[project]
authors = [{name = "Agentium", email = "contact@agentium.ru"}]
maintainers = [{name = "Agentium Team"}]
keywords = ["mcp", "documentation", "ai", "langchain"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Documentation",
    "Topic :: Software Development :: Libraries",
]
```

### URLs проекта
```toml
[project.urls]
Homepage = "https://github.com/agentium/superdocs"
Documentation = "https://superdocs.readthedocs.io"
Repository = "https://github.com/agentium/superdocs"
Issues = "https://github.com/agentium/superdocs/issues"
Changelog = "https://github.com/agentium/superdocs/blob/main/CHANGELOG.md"
```

## 🔧 Эволюция конфигурации

### Планируемые дополнения

#### 1. Расширенные зависимости
```toml
[project.optional-dependencies]
cache = ["redis>=4.0.0", "python-memcached>=1.59"]
monitoring = ["prometheus-client>=0.17.0"]
async-io = ["aiofiles>=23.0.0"]
performance = ["uvloop>=0.17.0", "orjson>=3.8.0"]
```

#### 2. Инструменты безопасности
```toml
[project.optional-dependencies]
security = [
    "bandit>=1.7.0",        # Сканер безопасности
    "safety>=2.3.0",        # Проверка уязвимостей
    "pip-audit>=2.6.0",     # Аудит зависимостей
]
```

#### 3. Плагинная система
```toml
[project.entry-points."superdocs.plugins"]
crawl4ai = "superdocs_crawl4ai:plugin"
confluence = "superdocs_confluence:plugin"
notion = "superdocs_notion:plugin"
```

## 📊 Сравнение с альтернативами

### pyproject.toml vs setup.py

| Характеристика | pyproject.toml | setup.py |
|----------------|----------------|-----------|
| Стандарт | PEP 518 (современный) | Устаревший |
| Читаемость | Высокая (TOML) | Низкая (Python код) |
| Валидация | Встроенная | Ручная |
| Инструменты | Все современные | Ограниченные |
| Размер | Компактный | Объемный |

### pyproject.toml vs setup.cfg

| Характеристика | pyproject.toml | setup.cfg |
|----------------|----------------|-----------|
| Формат | TOML | INI |
| Поддержка | Универсальная | Setuptools только |
| Стандартизация | PEP 518/621 | Неформальная |
| Будущее | Активное развитие | Устаревает |

## 🔒 Безопасность конфигурации

### Проверка целостности
```bash
# Валидация синтаксиса
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Проверка зависимостей
pip-audit --desc

# Сканирование безопасности
bandit -r superdocs/
```

### Лучшие практики
1. **Фиксированные версии**: Избегать `*` в версиях
2. **Проверенные источники**: Использовать только PyPI
3. **Минимальные зависимости**: Избегать bloat
4. **Регулярные обновления**: Следить за обновлениями безопасности

## 🚀 Автоматизация

### CI/CD интеграция
```yaml
# .github/workflows/test.yml
- name: Install dependencies
  run: |
    pip install -e ".[test]"
    
- name: Run tests
  run: |
    pytest tests/ --cov=superdocs
```

### Локальная разработка
```bash
# Установка в режиме разработки
pip install -e ".[test]"

# Запуск тестов
pytest

# Линтинг
ruff check superdocs/
```

Конфигурация в `pyproject.toml` обеспечивает современный, стандартизированный подход к управлению Python проектом и является основой для масштабируемого развития SuperDocs. 