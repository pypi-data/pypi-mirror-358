# Инструкции по публикации пакета superdocs

## Быстрая публикация (ручная)

### 1. Подготовка версии

```bash
# Обновить версию в pyproject.toml
# Например: version = "0.1.4"

# Создать коммит с обновлением версии
git add .
git commit -m "Bump version to 0.1.4"
git push origin main
```

### 2. Сборка пакета

```bash
# Активировать виртуальное окружение
source .venv/bin/activate

# Установить uv если не установлен
pip install uv

# Собрать пакет
uv build
```

### 3. Публикация в PyPI

```bash
# Установить twine
pip install twine

# Публикация с передачей токена напрямую
# ЗАМЕНИТЕ YOUR_PYPI_TOKEN на ваш реальный токен от PyPI
TWINE_USERNAME=__token__ TWINE_PASSWORD=YOUR_PYPI_TOKEN twine upload dist/*
```

### 4. Создание тега (опционально)

```bash
# Создать тег версии
git tag v0.1.4
git push origin v0.1.4
```

## Получение токена PyPI

1. Зайдите на https://pypi.org/manage/account/token/
2. Создайте новый токен с правами на загрузку
3. Скопируйте токен (начинается с `pypi-`)
4. Используйте его в команде выше

## Тестирование на Test PyPI

```bash
# Для тестирования используйте Test PyPI
TWINE_USERNAME=__token__ TWINE_PASSWORD=YOUR_TEST_PYPI_TOKEN twine upload --repository testpypi dist/*
```

## Автоматизация через GitLab CI/CD

Если хотите настроить автоматическую публикацию:

1. Зайдите в Settings → CI/CD → Variables в GitLab
2. Добавьте переменную `PYPI_TOKEN` со значением вашего токена
3. Отметьте "Protected" и "Masked"
4. Создание тега автоматически запустит публикацию

## Очистка старых сборок

```bash
# Удалить папку dist перед новой сборкой
rm -rf dist/
``` 