# _version.py - Управление версиями

## 🎯 Назначение

Централизованное управление версионированием SuperDocs. Определяет единый источник правды для версии пакета, используемой во всех компонентах системы - от CLI до setup.py и документации.

## 📋 Структура модуля

### Основная константа
```python
__version__ = "0.1.2"
```

**Характеристики**:
- Семантическое версионирование (SemVer)
- Строковый формат для совместимости
- Единый источник версии для всего проекта

### Дополнительные метаданные
```python
__version_info__ = (0, 1, 2)
```

**Назначение**: Программное сравнение версий в виде кортежа.

## 📊 Семантическое версионирование

### Формат версии: MAJOR.MINOR.PATCH

#### MAJOR (0)
- **Несовместимые изменения API**
- Кардинальные изменения архитектуры
- Пока 0 - продукт в активной разработке

#### MINOR (1) 
- **Новая функциональность** с обратной совместимостью
- Новые MCP инструменты
- Дополнительные транспорты или форматы

#### PATCH (2)
- **Исправления ошибок** без изменения API
- Оптимизации производительности
- Улучшения документации

## 🔧 Использование в проекте

### В CLI модуле
```python
from superdocs._version import __version__

parser.add_argument(
    "--version", "-V",
    action="version",
    version=f"mcpdoc {__version__}",
)
```

### В pyproject.toml
```toml
[project]
name = "superdocs"
version = "0.1.2"  # Должна совпадать с _version.py
```

### В setup скриптах
```python
from superdocs._version import __version__

setup(
    name="superdocs",
    version=__version__,
    # ...
)
```

## 🔄 Процесс обновления версии

### 1. Определение типа изменений
```bash
# Patch релиз (исправления)
0.1.2 → 0.1.3

# Minor релиз (новая функциональность)  
0.1.2 → 0.2.0

# Major релиз (breaking changes)
0.1.2 → 1.0.0
```

### 2. Обновление файла
```python
# _version.py
__version__ = "0.2.0"
__version_info__ = (0, 2, 0)
```

### 3. Синхронизация с pyproject.toml
```toml
[project]
version = "0.2.0"
```

### 4. Создание коммита и тега
```bash
git add superdocs/_version.py pyproject.toml
git commit -m "Bump version to 0.2.0"
git tag v0.2.0
git push origin main --tags
```

## 📈 История версий

### v0.1.2 (текущая)
- Исправления в CLI интерфейсе
- Улучшения документации
- Оптимизация обработки ошибок

### v0.1.1 
- Добавление SSE транспорта
- Улучшение splash экрана
- Расширение тестов

### v0.1.0
- Первый публичный релиз
- Базовая MCP функциональность
- YAML/JSON конфигурация

## 🛠️ Автоматизация версионирования

### Потенциальные улучшения

#### 1. Автоматическое обновление
```python
# scripts/bump_version.py
import re
from pathlib import Path

def bump_version(version_type: str):
    """Автоматически обновляет версию в файлах"""
    # Логика обновления _version.py и pyproject.toml
```

#### 2. Валидация синхронизации
```python
# tests/test_version.py
def test_version_sync():
    """Проверяет синхронизацию версий в разных файлах"""
    from superdocs._version import __version__
    import toml
    
    with open("pyproject.toml") as f:
        pyproject = toml.load(f)
    
    assert __version__ == pyproject["project"]["version"]
```

#### 3. Автоматический changelog
```python
def generate_changelog(version: str):
    """Генерирует changelog на основе git коммитов"""
    # Парсинг коммитов между тегами
    # Категоризация изменений
    # Генерация markdown
```

## 🔍 Программное использование версии

### Проверка совместимости
```python
from superdocs._version import __version_info__

def check_compatibility(required_version: tuple):
    """Проверяет совместимость версий"""
    return __version_info__ >= required_version

# Использование
if not check_compatibility((0, 2, 0)):
    raise Exception("Требуется SuperDocs >= 0.2.0")
```

### Условная функциональность
```python
from superdocs._version import __version_info__

def get_features():
    """Возвращает доступные функции в зависимости от версии"""
    features = ["list_doc_sources", "fetch_docs"]
    
    if __version_info__ >= (0, 2, 0):
        features.extend(["browse_index", "explore_hierarchy"])
        
    if __version_info__ >= (0, 3, 0):
        features.extend(["search_docs", "cache_management"])
        
    return features
```

### Метрики и аналитика
```python
import httpx
from superdocs._version import __version__

async def send_usage_metrics():
    """Отправляет анонимные метрики использования"""
    await httpx.post("https://analytics.example.com/usage", json={
        "version": __version__,
        "transport": "stdio",
        "sources_count": 3
    })
```

## 🔒 Безопасность версионирования

### Защита от подделки
```python
# Криптографическая подпись версии
import hashlib
import hmac

VERSION_KEY = "secret_key_for_version_validation"

def get_version_hash():
    """Возвращает хеш версии для валидации"""
    return hmac.new(
        VERSION_KEY.encode(),
        __version__.encode(),
        hashlib.sha256
    ).hexdigest()
```

### Валидация целостности
```python
def validate_version():
    """Проверяет, что версия не была изменена"""
    expected_hash = "expected_hash_for_current_version"
    actual_hash = get_version_hash()
    
    if actual_hash != expected_hash:
        raise Exception("Version integrity check failed")
```

## 📦 Интеграция с системами сборки

### GitHub Actions
```yaml
- name: Get version
  id: version
  run: |
    VERSION=$(python -c "from superdocs._version import __version__; print(__version__)")
    echo "::set-output name=version::$VERSION"

- name: Create release
  uses: actions/create-release@v1
  with:
    tag_name: v${{ steps.version.outputs.version }}
    release_name: Release ${{ steps.version.outputs.version }}
```

### GitLab CI
```yaml
variables:
  VERSION: $(python -c "from superdocs._version import __version__; print(__version__)")

release:
  script:
    - echo "Releasing version $VERSION"
    - twine upload dist/*
  only:
    - tags
```

## 🎯 Планы развития версионирования

### Ближайшие релизы

#### v0.2.0 - Иерархическая навигация
- `browse_index()` MCP инструмент
- `explore_hierarchy()` функциональность
- Расширенное кэширование

#### v0.3.0 - Поиск и аналитика
- `search_docs()` инструмент
- Метрики использования
- Производительные улучшения

#### v1.0.0 - Стабильный API
- Замораживание публичного API
- Полная документация
- Enterprise функции

### Долгосрочные планы
- Плагинная архитектура (v2.0.0)
- Распределенное кэширование (v2.1.0)
- AI-powered поиск (v3.0.0)

Модуль `_version.py` обеспечивает профессиональное управление жизненным циклом SuperDocs и является основой для надежного релизного процесса. 