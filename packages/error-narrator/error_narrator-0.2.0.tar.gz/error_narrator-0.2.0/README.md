# Error Narrator 🤖

**Error Narrator** — это умная Python-библиотека, которая превращает непонятные трейсбеки ошибок в ясные, структурированные объяснения с помощью искусственного интеллекта. Забудьте о долгом гуглении ошибок — получите причину, место и готовое решение прямо в вашей консоли!

[![PyPI version](https://badge.fury.io/py/error-narrator.svg)](https://badge.fury.io/py/error-narrator)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https.github.com/Zahabsbs/error-narrator/blob/main/LICENSE)

## 🚀 Основные возможности

- **Анализ ошибок с помощью ИИ:** Получайте подробный разбор любого трейсбека.
- **Структурированный ответ:** Объяснение всегда включает:
  - **🎯 Причину ошибки:** Что именно пошло не так.
  - **📍 Место ошибки:** Точный файл и строка с фрагментом кода.
  - **🛠️ Предлагаемое исправление:** Готовый для копирования код, который решает проблему.
  - **🎓 Обучающий момент:** Краткое объяснение концепции, чтобы избегать подобных ошибок в будущем.
- **Поддержка нескольких провайдеров:**
  - **`gradio` (по умолчанию):** Бесплатный доступ к моделям на Hugging Face Spaces. Отлично для быстрого старта.
  - **`openai`:** Используйте мощные модели, такие как GPT-3.5 или GPT-4, для более точных и надежных ответов (требуется API-ключ).
- **Синхронный и асинхронный режимы:** Используйте библиотеку в любом проекте.

## 📦 Установка

```bash
pip install error-narrator
```

Для работы с OpenAI необходимо также установить соответствующую зависимость, которая включена в `pyproject.toml`.

## ⚙️ Как использовать

### Шаг 1: Настройка окружения

Для провайдера `openai` необходимо установить ваш API-ключ в качестве переменной окружения:
```bash
export OPENAI_API_KEY='sk-...'
```
Для приватных `gradio` репозиториев может понадобиться ключ Hugging Face:
```bash
export HUGGINGFACE_API_KEY='hf_...'
```

### Шаг 2: Использование в коде

Это очень просто. Оберните ваш код в `try...except`, поймайте исключение и передайте его трейсбек в `ErrorNarrator`.

```python
import traceback
from error_narrator import ErrorNarrator

def some_buggy_function():
    # Пример кода, который вызовет ошибку
    data = {'user': 'Alice'}
    print(data['age']) # KeyError

if __name__ == "__main__":
    try:
        some_buggy_function()
    except Exception:
        tb_str = traceback.format_exc()

        print("\n--- 😱 Произошла ошибка! Анализирую с помощью AI... ---\n")

        # --- Вариант 1: Использование бесплатного провайдера Gradio (по умолчанию) ---
        narrator_free = ErrorNarrator()
        narrator_free.explain_and_print(tb_str)

        print("\n--- 🚀 Анализ с помощью более мощной модели OpenAI... ---\n")

        # --- Вариант 2: Использование провайдера OpenAI ---
        # Убедитесь, что ключ OPENAI_API_KEY установлен
        try:
            narrator_pro = ErrorNarrator(provider='openai', model_id='gpt-3.5-turbo')
            narrator_pro.explain_and_print(tb_str)
        except Exception as e:
            print(f"Не удалось запустить OpenAI: {e}")

```
## 📈 Будущие улучшения

- Добавление поддержки других AI-провайдеров (Anthropic, Gemini).

## 🤝 Вклад

Мы будем рады вашему вкладу! Если у вас есть идеи по улучшению, пожалуйста, создавайте issue или pull request.