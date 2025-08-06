# 🤖 Multi-Bot Twitter System с ENV конфигурацией

## 🚀 Быстрый старт

### 1. Создание конфигурации

```bash
# Создать шаблон .env файла
python multi_bot_system.py create_env

# Создать инструменты быстрой настройки
python multi_bot_system.py create_tools
```

### 2. Настройка через мастер

```bash
# Интерактивный менеджер
python bot_manager.py

# Или мастер быстрой настройки
python bot_manager.py wizard
```

### 3. Запуск системы

```bash
# Запуск всех ботов
python multi_bot_system.py run

# Тест отдельного бота
python multi_bot_system.py test 0
```

## ⚙️ Быстрая настройка через .env

### Основные переменные

```env
# Аккаунты для мониторинга
MONITORED_ACCOUNTS=elonmusk,VitalikButerin,cz_binance,saylor

# Количество ботов
BOT_COUNT=3

# Глобальные настройки
GLOBAL_DRY_RUN=false
MAX_CONCURRENT_BOTS=3
```

### Настройка отдельного бота

```env
# Бот 1 - DEVINVEST
BOT1_NAME=DEVINVEST_Official
BOT1_AUTH_PATH=auth_devinvest_main
BOT1_DEFAULT_STYLE=educational
BOT1_DEFAULT_TONE=professional
BOT1_TARGET_ACCOUNTS=VitalikButerin,saylor
BOT1_PRIORITY_KEYWORDS=defi,web3,blockchain,building
BOT1_ENABLED=true
```

## 🎛️ Быстрые команды

### Изменение стилей

```bash
# Установить юмористический стиль для бота 2
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('BOT2_DEFAULT_STYLE', 'humorous')"

# Все доступные стили
# neutral, humorous, analytical, educational, supportive, provocative, ironic
```

### Изменение целевых аккаунтов

```bash
# Бот 1 отвечает только на Vitalik и Saylor
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('BOT1_TARGET_ACCOUNTS', 'VitalikButerin,saylor')"

# Бот 2 отвечает на всех (пустое значение)
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('BOT2_TARGET_ACCOUNTS', '')"
```

### Изменение ключевых слов

```bash
# Приоритетные слова для бота
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('BOT1_PRIORITY_KEYWORDS', 'defi,web3,blockchain')"

# Слова для избегания
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('BOT2_AVOID_KEYWORDS', 'scam,pump,dump')"
```

### Режимы работы

```bash
# Включить тестовый режим для всех
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('GLOBAL_DRY_RUN', 'true')"

# Выключить конкретного бота
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('BOT3_ENABLED', 'false')"
```

## 📝 Готовые пресеты

### 🎯 Целевой режим (каждый бот на своих аккаунтах)

```bash
python bot_manager.py wizard
# Выбрать: 1. Target Mode
```

**Результат:**
- Бот 1: VitalikButerin, saylor, brian_armstrong + образовательный стиль
- Бот 2: elonmusk, APompliano, DocumentingBTC + юмористический стиль  
- Бот 3: stani, haydenzadams, AndreCronjeTech + аналитический стиль

### 🌐 Режим вещания (все боты на всех аккаунтах)

```bash
python bot_manager.py wizard  
# Выбрать: 2. Broadcast Mode
```

### 🧪 Тестовый режим

```bash
python bot_manager.py wizard
# Выбрать: 3. Test Mode
```

**Настройки:**
- Все боты в DRY RUN
- Видимые браузеры
- Быстрые циклы (10 минут)

### 🔥 Агрессивный режим

```bash
python bot_manager.py wizard
# Выбрать: 4. Aggressive Mode
```

**Настройки:**
- Циклы каждые 20 минут
- До 2 ответов за цикл
- До 50 ответов в день
- Низкий порог уверенности (0.6)

## 🚨 Экстренное управление

### Остановка всех ботов

```bash
# Создать файл экстренной остановки
touch STOP_ALL_BOTS

# Или через менеджер
python bot_manager.py emergency
```

### Включение тестового режима

```bash
# Через переменную окружения
export GLOBAL_DRY_RUN=true

# Или через .env файл
echo "GLOBAL_DRY_RUN=true" >> .env
```

## 📊 Мониторинг

### Статус всех ботов

```bash
python bot_manager.py status
```

**Пример вывода:**
```
🤖 Multi-Bot Status
==================
📊 Global Settings:
  Monitored Accounts: elonmusk,VitalikButerin,cz_binance
  Max Concurrent: 3
  Daily Limit: 100
  Global Dry Run: false

Bot 1: 🟢 DEVINVEST_Official
  Status: ENABLED
  Mode: 🔴 LIVE
  Style: educational
  Targets: VitalikButerin,saylor
  Keywords: defi,web3,blockchain
```

### Текущая конфигурация

```bash
python multi_bot_system.py show_config
```

## 🔧 Продвинутые настройки

### Настройка промптов

```env
BOT1_PERSONA_PROMPT=Ты голос DEVINVEST. Через твои посты люди видят, что Web3 может быть безопасным, честным и полезным. Пиши четко, без лишнего шума.

BOT2_PERSONA_PROMPT=Ты мемный крипто-твиттерщик, который жжет без оглядки. Каждый твой твит - это укол по боли рынка.
```

### Запасные стили

```env
BOT1_BACKUP_STYLES=analytical,supportive,neutral
BOT2_BACKUP_STYLES=provocative,ironic,humorous
```

### Поведенческие настройки

```env
BOT1_CYCLE_INTERVAL=35              # Минуты между циклами
BOT1_MAX_RESPONSES_PER_CYCLE=1      # Ответов за цикл
BOT1_MAX_DAILY_RESPONSES=25         # Дневной лимит
BOT1_CONFIDENCE_THRESHOLD=0.8       # Порог уверенности AI
```

### Таргетинг

```env
# Целевые аккаунты (пусто = все)
BOT1_TARGET_ACCOUNTS=VitalikButerin,saylor

# Приоритетные ключевые слова
BOT1_PRIORITY_KEYWORDS=defi,web3,blockchain,building

# Слова для избегания
BOT1_AVOID_KEYWORDS=scam,pump,dump,moon
```

## 🎨 Доступные стили и тона

### Стили ответов

- **neutral** - Сбалансированные ответы
- **humorous** - Юмор и мемы
- **analytical** - Данные и факты
- **educational** - Обучающие ответы
- **supportive** - Поддерживающие
- **provocative** - Провокационные вопросы
- **ironic** - Ирония и сарказм

### Тона

- **friendly** - Дружелюбный
- **professional** - Профессиональный
- **sarcastic** - Саркастический
- **witty** - Остроумный
- **casual** - Неформальный
- **aggressive** - Агрессивный

## 🔄 Горячая перезагрузка конфигурации

Боты автоматически перезагружают конфигурацию каждые 5 минут. Можно:

1. **Изменить .env файл** - изменения применятся через 5 минут
2. **Использовать bot_manager.py** - изменения применятся немедленно
3. **Использовать быстрые команды** - мгновенное применение

```bash
# Изменить стиль бота 2 на лету
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('BOT2_DEFAULT_STYLE', 'humorous')"

# Проверить что изменилось
python bot_manager.py status
```

## 🚀 Bash алиасы для быстрого управления

```bash
# Загрузить алиасы
source bot_commands.sh

# Использовать
bot-status          # Показать статус
bot-humor           # Бот 2 в юмористический режим
bot-dry             # Все боты в тестовый режим
bot-start           # Запустить систему
bot-stop            # Остановить все боты
```

## 📁 Структура файлов

```
your_project/
├── multi_bot_system.py      # Основная система ботов
├── bot_manager.py           # Менеджер конфигурации
├── .env                     # Конфигурация
├── .env.multi_bot          # Шаблон конфигурации
├── bot_commands.sh         # Bash алиасы
├── auth_devinvest_main/    # Авторизация бота 1
├── auth_meme_account/      # Авторизация бота 2
├── auth_analyst_account/   # Авторизация бота 3
├── tweet_history_*.json   # История каждого бота
└── STOP_ALL_BOTS          # Файл экстренной остановки
```

## 🔍 Примеры использования

### Запуск в тестовом режиме

```bash
# Быстрая настройка
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('GLOBAL_DRY_RUN', 'true')"

# Запуск
python multi_bot_system.py run
```

### Настройка мем-бота

```bash
# Юмористический стиль, саркастический тон
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('BOT2_DEFAULT_STYLE', 'humorous'); m.update_setting('BOT2_DEFAULT_TONE', 'sarcastic')"

# Целевые аккаунты - мемеры и хайперы
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('BOT2_TARGET_ACCOUNTS', 'elonmusk,APompliano')"

# Ключевые слова мемов
python -c "from bot_manager import BotManager; m=BotManager(); m.update_setting('BOT2_PRIORITY_KEYWORDS', 'moon,hodl,diamond hands,wen,ngmi')"
```

### Быстрое переключение режимов

```bash
# Утром - консервативный режим
python bot_manager.py wizard  # Выбрать 5

# Днем - агрессивный режим  
python bot_manager.py wizard  # Выбрать 4

# Вечером - тестовый режим
python bot_manager.py wizard  # Выбрать 3
```

## 🛠️ Устранение проблем

### Ошибка "multi_bot_launcher is not defined"

**Решение:** Файл был переименован в `multi_bot_system.py`

```bash
# Правильный запуск
python multi_bot_system.py run

# Вместо старого
python multi_bot_launcher.py launch
```

### Боты не запускаются

**Проверить:**

```bash
# Статус конфигурации
python bot_manager.py status

# Включены ли боты
python -c "from bot_manager import BotManager; m=BotManager(); print('Bot1:', m.get_setting('BOT1_ENABLED')); print('Bot2:', m.get_setting('BOT2_ENABLED'))"

# Есть ли файл остановки
ls STOP_ALL_BOTS
```

### Быстрый сброс к настройкам по умолчанию

```bash
python bot_manager.py emergency
# Выбрать: 5. Reset to Defaults
```

## 🎯 Лучшие практики

1. **Начинайте с тестового режима** - `GLOBAL_DRY_RUN=true`
2. **Используйте целевые аккаунты** - не перегружайте систему
3. **Настройте ключевые слова** - фильтруйте релевантный контент
4. **Мониторьте статус** - регулярно проверяйте `bot-status`
5. **Быстрые изменения** - используйте `bot_manager.py` вместо ручного редактирования .env