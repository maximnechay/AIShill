import os
import ssl
import certifi
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# Исправление SSL в самом начале
os.environ["SSL_CERT_FILE"] = certifi.where()

from playwright.async_api import async_playwright
import time
import logging
import asyncio
from reply_engine import ReplyEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Более консервативный список аккаунтов для стабильности
USERNAMES = [
    # Топ криптолидеры (проверенные)
    "elonmusk",
    "chainlink",
    "cz_binance",
    "saylor",
    # Криптоинфлюенсеры
    "APompliano",
    "DocumentingBTC",
    "DegenerateNews",
    "RaoulGMI",
    "balajis",
    # Основатели и CEO
    "brian_armstrong",
    "justinsuntron",
    "CoinMarketCap",
    # Трейдеры
    "CryptoCapo_",
    "pentosh1",
    "crypto_birb",
    # Медиа
    "cointelegraph",
    "BitcoinMagazine",
    "coindesk",
    # DeFi
    "solana",
    "AltcoinGordon",
    "kucoincom",
]


class AutoCycleResponder:
    def __init__(self):
        print(f"🔒 SSL сертификаты: {os.environ.get('SSL_CERT_FILE')}")

        self.reply_engine = None
        self.dry_run = False  # LIVE режим
        self.show_browser = True  # ВИДИМЫЙ браузер для наблюдения

        # История обработанных твитов
        self.history_file = Path("tweet_history.json")
        self.processed_tweets = self.load_history()

        # Настройки циклов - БОЛЕЕ КОНСЕРВАТИВНЫЕ для стабильности
        self.cycle_interval_minutes = 20  # Увеличен интервал
        self.max_responses_per_cycle = 1  # Уменьшен лимит для стабильности
        self.max_daily_responses = 60  # Разумный лимит
        self.max_tweets_per_account = 5  # Меньше твитов для быстроты
        self.min_confidence_threshold = 0.7  # Выше порог для качества

        # Настройки поиска - УПРОЩЕННЫЕ
        self.search_strategies = [
            {"scroll_depth": 800, "wait_time": 2},  # Быстрый поиск
            {"scroll_depth": 1600, "wait_time": 3},  # Средний поиск
        ]

        # Контроль контекстов браузера - ИСПРАВЛЕНО
        self.playwright = None
        self.browser_context = None
        self.context_lock = asyncio.Lock()

        # Статистика - ИСПРАВЛЕННАЯ ИНИЦИАЛИЗАЦИЯ
        self.stats = {
            "total_cycles": 0,
            "total_responses": 0,
            "responses_today": 0,
            "last_reset_date": datetime.now().date().isoformat(),
            "start_time": datetime.now().isoformat(),
            "accounts_stats": {},
            "search_efficiency": {
                "cycles_with_responses": 0,
                "cycles_without_responses": 0,
                "average_tweets_per_cycle": 0,
            },
        }

        # Инициализируем статистику для каждого аккаунта
        for username in USERNAMES:
            self.stats["accounts_stats"][username] = {
                "checked": 0,
                "responded": 0,
                "tweets_found": 0,  # ИСПРАВЛЕНО: добавлено поле
            }

        self.load_stats()

    def load_history(self):
        """Загрузка истории обработанных твитов"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    processed = set(data.get("processed_tweets", []))

                    # Очищаем старые записи (старше 2 дней для большего поиска)
                    cutoff_date = datetime.now() - timedelta(days=2)
                    cleaned = set()

                    for tweet_id in processed:
                        if tweet_id in data.get("metadata", {}):
                            tweet_date = datetime.fromisoformat(
                                data["metadata"][tweet_id].get("date", "2020-01-01")
                            )
                            if tweet_date > cutoff_date:
                                cleaned.add(tweet_id)

                    print(
                        f"📚 Загружено {len(cleaned)} ID обработанных твитов (очищено {len(processed) - len(cleaned)} старых)"
                    )
                    return cleaned

            except Exception as e:
                print(f"⚠️ Ошибка загрузки истории: {e}")

        print("📚 Создана новая история твитов")
        return set()

    def save_history(self):
        """Сохранение истории обработанных твитов"""
        try:
            data = {
                "processed_tweets": list(self.processed_tweets),
                "metadata": {},
                "last_updated": datetime.now().isoformat(),
                "total_processed": len(self.processed_tweets),
            }

            current_date = datetime.now().isoformat()
            for tweet_id in self.processed_tweets:
                data["metadata"][tweet_id] = {"date": current_date}

            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ Ошибка сохранения истории: {e}")

    def load_stats(self):
        """Загрузка статистики"""
        stats_file = Path("responder_stats.json")
        if stats_file.exists():
            try:
                with open(stats_file, "r", encoding="utf-8") as f:
                    saved_stats = json.load(f)

                    # Проверяем, не новый ли день
                    last_date = saved_stats.get("last_reset_date")
                    today = datetime.now().date().isoformat()

                    if last_date != today:
                        saved_stats["responses_today"] = 0
                        saved_stats["last_reset_date"] = today
                        print("🌅 Новый день - сброс дневной статистики")

                    # ИСПРАВЛЕНО: Безопасное обновление статистики аккаунтов
                    if "accounts_stats" not in saved_stats:
                        saved_stats["accounts_stats"] = {}

                    for username in USERNAMES:
                        if username not in saved_stats["accounts_stats"]:
                            saved_stats["accounts_stats"][username] = {
                                "checked": 0,
                                "responded": 0,
                                "tweets_found": 0,
                            }
                        else:
                            # Добавляем недостающие поля
                            if (
                                "tweets_found"
                                not in saved_stats["accounts_stats"][username]
                            ):
                                saved_stats["accounts_stats"][username][
                                    "tweets_found"
                                ] = 0

                    self.stats.update(saved_stats)
                    print(
                        f"📊 Загружена статистика: {self.stats['total_responses']} ответов всего, {self.stats['responses_today']} сегодня"
                    )

            except Exception as e:
                print(f"⚠️ Ошибка загрузки статистики: {e}")

    def save_stats(self):
        """Сохранение статистики"""
        try:
            stats_file = Path("responder_stats.json")
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения статистики: {e}")

    def generate_tweet_id(self, tweet_text, username):
        """Генерация уникального ID твита"""
        content = f"{tweet_text.strip()}{username}".encode("utf-8")
        return hashlib.md5(content).hexdigest()[:12]

    def is_tweet_processed(self, tweet_id):
        """Проверка, был ли твит уже обработан"""
        return tweet_id in self.processed_tweets

    def mark_tweet_processed(self, tweet_id):
        """Отметить твит как обработанный"""
        self.processed_tweets.add(tweet_id)
        self.save_history()

    def can_respond_today(self):
        """Проверка, можно ли еще отвечать сегодня"""
        return self.stats["responses_today"] < self.max_daily_responses

    async def get_reply_engine(self):
        """Асинхронная инициализация ReplyEngine"""
        if self.reply_engine is None:
            try:
                self.reply_engine = ReplyEngine()
                logger.info("✅ AI движок инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации AI: {e}")
                raise
        return self.reply_engine

    def get_tweet_style(self, tweet_text):
        """Улучшенная классификация стиля твита"""
        text_lower = tweet_text.lower()

        if any(
            word in text_lower
            for word in ["moon", "🚀", "pump", "bull", "rally", "ath", "hodl"]
        ):
            return "humorous"
        elif any(
            word in text_lower
            for word in ["crash", "bear", "down", "dead", "dump", "recession"]
        ):
            return "analytical"
        elif any(
            word in text_lower
            for word in ["building", "future", "progress", "development", "innovation"]
        ):
            return "supportive"
        elif any(
            word in text_lower
            for word in ["scaling", "technology", "blockchain", "consensus", "protocol"]
        ):
            return "educational"
        elif any(
            word in text_lower
            for word in ["regulation", "sec", "government", "policy", "legal"]
        ):
            return "analytical"
        elif any(
            word in text_lower for word in ["defi", "nft", "web3", "metaverse", "dao"]
        ):
            return "educational"
        else:
            return "neutral"

    async def generate_response(self, tweet_text, username):
        """Асинхронная генерация ответа с учетом автора"""
        try:
            engine = await self.get_reply_engine()
            style = self.get_tweet_style(tweet_text)

            # Контекст в зависимости от автора
            if username in ["elonmusk", "saylor"]:
                audience = "mainstream"
            elif username in ["VitalikButerin", "stani", "haydenzadams"]:
                audience = "technical"
            else:
                audience = "crypto"

            result = await engine.generate_reply(
                tweet_text=tweet_text,
                style=style,
                audience=audience,
                reply_length="short",
            )

            return result["reply"], style, result.get("confidence_score", 0)

        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return None, None, 0

    class AutoCycleResponder:
        def __init__(self):
            self.browser_context = None
            self.playwright = None
            self.context_lock = asyncio.Lock()
            self.show_browser = True  # или False

    async def get_browser_context(self):
        async with self.context_lock:
            try:
                if self.browser_context:
                    page = await self.browser_context.new_page()
                    await page.close()
                    return self.browser_context
            except Exception as e:
                print(f"⚠️ Контекст не работает, пересоздаём: {e}")
                try:
                    await self.browser_context.close()
                except:
                    pass
                self.browser_context = None

            if not self.playwright:
                self.playwright = await async_playwright().start()

            print("🌐 Перезапуск Chromium с auth/")

            self.browser_context = (
                await self.playwright.chromium.launch_persistent_context(
                    "auth",
                    headless=not self.show_browser,
                    args=[
                        "--no-sandbox",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                    ],
                )
            )
            print("✅ Новый контекст готов")
            return self.browser_context

    async def check_and_fix_auth(self):
        """УЛУЧШЕННАЯ проверка авторизации с автоматическим исправлением"""
        try:
            print("🔐 Проверяем авторизацию...")

            context = await self.get_browser_context()
            page = await context.new_page()

            try:
                await page.goto("https://x.com/home", timeout=15000)
                await asyncio.sleep(3)

                current_url = page.url
                title = await page.title()

                print(f"📍 URL: {current_url}")
                print(f"📋 Title: {title}")

                # Проверяем признаки успешной авторизации
                if (
                    "home" in current_url
                    and "login" not in current_url
                    and "i/flow" not in current_url
                    and not title.startswith(("Log in", "Вход"))
                ):

                    # Дополнительная проверка - наличие навигации
                    nav_count = await page.locator("nav").count()
                    print(f"🧭 Найдено nav элементов: {nav_count}")

                    if nav_count > 0:
                        print("✅ Авторизован!")
                        return True

                print("❌ НЕ АВТОРИЗОВАН!")
                print("\n🔧 КАК ИСПРАВИТЬ:")
                print("1. Остановите бота (Ctrl+C)")
                print("2. Запустите: python login.py")
                print("3. Войдите в свой Twitter аккаунт")
                print("4. Запустите бота снова")
                print()

                # Спрашиваем, хочет ли пользователь войти сейчас
                if not self.show_browser:  # Если браузер скрытый
                    print("💡 Хотите войти прямо сейчас?")
                    choice = input("Открыть форму входа? [y/N]: ").strip().lower()

                    if choice == "y":
                        return await self.interactive_login(page)

                return False

            finally:
                await page.close()

        except Exception as e:
            print(f"❌ Ошибка проверки авторизации: {e}")
            return False

    async def interactive_login(self, page):
        """Интерактивный вход прямо из бота"""
        try:
            print("\n🔐 БЫСТРЫЙ ВХОД В TWITTER")
            print("=" * 30)

            # Переходим на страницу входа
            await page.goto("https://x.com/i/flow/login", timeout=15000)
            await asyncio.sleep(3)

            print("📋 В открывшемся окне:")
            print("1. Введите логин/email")
            print("2. Введите пароль")
            print("3. Пройдите проверки")
            print("4. Нажмите Enter здесь когда войдете")

            # Показываем браузер для входа
            await page.evaluate("() => { window.focus(); }")

            # Ждем ввода пользователя
            input("\n⏸ Нажмите Enter ПОСЛЕ успешного входа: ")

            # Проверяем результат
            await page.goto("https://x.com/home", timeout=15000)
            await asyncio.sleep(3)

            current_url = page.url
            nav_count = await page.locator("nav").count()

            if "home" in current_url and nav_count > 0:
                print("✅ Вход успешен!")
                return True
            else:
                print("❌ Вход не удался")
                return False

        except Exception as e:
            print(f"❌ Ошибка интерактивного входа: {e}")
            return False

    async def find_new_tweets(self, username, max_check=5, strategy_index=0):
        """ИСПРАВЛЕННАЯ функция поиска твитов с улучшенной обработкой ошибок"""
        new_tweets = []

        try:
            strategy = self.search_strategies[
                min(strategy_index, len(self.search_strategies) - 1)
            ]

            # Получаем контекст браузера
            context = await self.get_browser_context()
            if not context:
                print(f"❌ @{username}: Не удалось получить контекст браузера")
                return []

            page = await context.new_page()

            # Устанавливаем user agent
            await page.set_extra_http_headers(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )

            try:
                # Переход на профиль
                profile_url = f"https://x.com/{username}"
                print(f"🌐 Переход на {profile_url}")
                await page.goto(profile_url, timeout=20000)
                await asyncio.sleep(strategy["wait_time"])

                # Проверяем, что профиль загрузился
                current_url = page.url
                if "login" in current_url or "i/flow" in current_url:
                    print(f"❌ @{username}: Требуется авторизация")
                    return []

                page_title = await page.title()
                if (
                    "doesn't exist" in page_title.lower()
                    or "suspended" in page_title.lower()
                ):
                    print(f"❌ @{username}: Профиль недоступен ({page_title})")
                    return []

                print(f"📋 Заголовок страницы: {page_title}")

                # Загрузка твитов
                print(f"📜 Загрузка твитов (глубина: {strategy['scroll_depth']}px)")
                await page.evaluate(f"window.scrollTo(0, {strategy['scroll_depth']})")
                await asyncio.sleep(strategy["wait_time"])

                # Поиск статей
                articles = await page.locator("article").all()
                print(f"🔍 Найдено {len(articles)} статей для проверки")

                if len(articles) == 0:
                    print(
                        f"⚠️ @{username}: Статьи не найдены, возможно проблемы с загрузкой"
                    )
                    # Попробуем еще раз прокрутить
                    await page.evaluate("window.scrollTo(0, 1200)")
                    await asyncio.sleep(3)
                    articles = await page.locator("article").all()
                    print(f"🔄 После повторной прокрутки: {len(articles)} статей")

                for i, article in enumerate(articles[:max_check]):
                    try:
                        # Получаем весь текст статьи
                        full_text = await article.inner_text()

                        # Отладочная информация
                        if i < 2:  # Показываем первые 2 статьи для отладки
                            print(f"📄 Статья {i+1}: {full_text[:100]}...")

                        # Проверяем, что это не реплай и не реклама
                        if (
                            full_text.lower().startswith("replying to")
                            or "promoted" in full_text.lower()
                            or "ad" in full_text.lower()
                        ):
                            continue

                        # Ищем текст твита
                        tweet_text_elem = article.locator('[data-testid="tweetText"]')
                        if await tweet_text_elem.count() > 0:
                            parts = await tweet_text_elem.evaluate_all(
                                "els => els.map(el => el.innerText.trim())"
                            )
                            tweet_text = " ".join(parts).strip()

                        else:
                            # Альтернативный способ извлечения текста
                            lines = full_text.split("\n")
                            potential_tweet_lines = []

                            for line in lines:
                                line = line.strip()
                                if (
                                    line
                                    and len(line) > 10
                                    and not line.startswith("@")
                                    and not line.endswith("h")  # время
                                    and not line.endswith("m")
                                    and not line.endswith("s")
                                    and line
                                    not in ["Reply", "Retweet", "Like", "Share"]
                                ):
                                    potential_tweet_lines.append(line)

                                if (
                                    len(potential_tweet_lines) >= 2
                                ):  # Берем первые 2 содержательные строки
                                    break

                            tweet_text = " ".join(potential_tweet_lines)

                        # Проверяем качество твита
                        if (
                            len(tweet_text) > 20  # Минимальная длина
                            and not tweet_text.startswith("RT @")  # Не ретвит
                            and len(tweet_text) < 600
                        ):  # Не слишком длинный

                            tweet_id = self.generate_tweet_id(tweet_text, username)

                            # Проверяем, не обрабатывали ли уже
                            if not self.is_tweet_processed(tweet_id):
                                # Проверяем, подходит ли твит для ответа
                                if self.is_good_tweet_for_reply(tweet_text):
                                    tweet = {
                                        "id": tweet_id,
                                        "text": tweet_text,
                                        "username": username,
                                        "found_at": datetime.now().isoformat(),
                                        "article_index": i,
                                    }
                                    new_tweets.append(tweet)
                                    print(
                                        f"🆕 Новый твит от @{username}: {tweet_text[:60]}..."
                                    )
                                else:
                                    print(
                                        f"⏭️ Твит не подходит для ответа: {tweet_text[:500]}..."
                                    )
                            else:
                                print(f"⏭️ Твит уже обработан: {tweet_text[:50]}...")

                    except Exception as e:
                        print(f"⚠️ Ошибка обработки статьи {i}: {e}")
                        continue

                # ИСПРАВЛЕНО: Безопасное обновление статистики
                if username in self.stats["accounts_stats"]:
                    self.stats["accounts_stats"][username]["checked"] += 1
                    self.stats["accounts_stats"][username]["tweets_found"] += len(
                        new_tweets
                    )

            except Exception as e:
                print(f"❌ Ошибка поиска твитов @{username}: {e}")
                import traceback

                print(f"Детали ошибки: {traceback.format_exc()}")
            finally:
                try:
                    await page.close()
                    print(f"✅ Страница для @{username} закрыта")
                except Exception as e:
                    print(f"⚠️ Ошибка закрытия страницы: {e}")

        except Exception as e:
            print(f"💥 Критическая ошибка для @{username}: {e}")
            import traceback

            print(f"Детали критической ошибки: {traceback.format_exc()}")

        return new_tweets

    def is_good_tweet_for_reply(self, tweet_text):
        """Проверка, подходит ли твит для ответа"""
        text_lower = tweet_text.lower()

        # Исключаем неподходящие твиты
        bad_indicators = [
            "gm",
            "gn",
            "good morning",
            "good night",
            "happy birthday",
            "rip",
            "rest in peace",
            "join my",
            "get your",
            "claim now",
            "link in bio",
            "dm me",
            "check out",
        ]

        if any(indicator in text_lower for indicator in bad_indicators):
            return False

        # Ищем хорошие темы для ответа
        good_indicators = [
            "bitcoin",
            "btc",
            "ethereum",
            "eth",
            "crypto",
            "blockchain",
            "price",
            "market",
            "trading",
            "bull",
            "bear",
            "pump",
            "dump",
            "ai",
            "artificial intelligence",
            "technology",
            "innovation",
            "defi",
            "nft",
            "web3",
            "dao",
            "metaverse",
            "protocol",
            "inflation",
            "fed",
            "economy",
            "finance",
            "investment",
            # Добавлено для DEVINVEST и мемкоинов:
            "tokenization",
            "token",
            "tge",
            "pre-sale",
            "airdrop",
            "drop",
            "kyc",
            "launchpad",
            "founder",
            "dev",
            "build",
            "builder",
            "startup",
            "founders",
            "launch",
            "rugpull",
            "scam",
            "verified",
            "trust",
            "team",
            "project",
            "community",
            "decentralized",
            "governance",
            "voting",
            "dapp",
            "yield",
            "meme",
            "memecoin",
            "shitcoin",
            "solana",
            "ecosystem",
            "utility",
            "investor",
            "developers",
            "whitelist",
            "dao vote",
            "smart contract",
            "audit",
            "liquidity",
            "dex",
            "dvi",
            "devinvest",
            "devinvestcoin",
        ]

        has_good_topic = any(indicator in text_lower for indicator in good_indicators)
        is_good_length = 20 <= len(tweet_text) <= 600
        has_substance = len(tweet_text.split()) >= 4

        return has_good_topic and is_good_length and has_substance

    async def send_response_to_tweet(self, tweet, response_text):
        """ИСПРАВЛЕННАЯ отправка ответа"""
        try:
            context = await self.get_browser_context()
            page = await context.new_page()

            try:
                # Переход на профиль
                profile_url = f"https://x.com/{tweet['username']}"
                await page.goto(profile_url, timeout=12000)
                await asyncio.sleep(3)

                # Загрузка твитов
                await page.evaluate("window.scrollTo(0, 800)")
                await asyncio.sleep(2)

                # Поиск нужного твита по содержимому
                articles = await page.locator("article").all()

                target_article = None
                for article in articles:
                    try:
                        article_text = await article.inner_text()
                        if tweet["text"][:50] in article_text:
                            target_article = article
                            break
                    except:
                        continue

                if target_article:
                    # Кликаем Reply
                    reply_button = target_article.locator('[data-testid="reply"]')
                    if await reply_button.count() > 0:
                        await reply_button.click()
                        await asyncio.sleep(3)

                        # Вводим текст
                        compose_textbox = page.locator(
                            '[data-testid="tweetTextarea_0"]'
                        )
                        if await compose_textbox.count() > 0:
                            await compose_textbox.fill(response_text)
                            await asyncio.sleep(2)

                            # ДОБАВЛЯЕМ ПРОБЕЛ для активации поля
                            await compose_textbox.type(" ")
                            await asyncio.sleep(0.5)

                            # ДОПОЛНИТЕЛЬНЫЙ КЛИК НА ПОЛЕ
                            await compose_textbox.click()
                            await asyncio.sleep(1)

                            if not self.dry_run:
                                # Отправляем
                                tweet_button = page.locator(
                                    '[data-testid="tweetButton"]'
                                )
                                if await tweet_button.count() > 0:
                                    await tweet_button.click()
                                    await asyncio.sleep(3)
                                    return True
                            else:
                                print("🧪 DRY RUN: Ответ не отправлен")
                                return True

                return False

            finally:
                await page.close()

        except Exception as e:
            print(f"💥 Критическая ошибка отправки: {e}")
            return False

    async def smart_account_search(self):
        """УПРОЩЕННЫЙ умный поиск по аккаунтам"""
        all_candidates = []

        # Сортируем аккаунты по эффективности
        sorted_accounts = sorted(
            USERNAMES,
            key=lambda x: self.stats["accounts_stats"]
            .get(x, {})
            .get("tweets_found", 0),
            reverse=True,
        )

        # Проверяем аккаунты пока не найдем достаточно кандидатов
        for username in sorted_accounts:
            if len(all_candidates) >= self.max_responses_per_cycle * 3:
                break

            try:
                print(f"🔍 Проверяем @{username}...")

                # Используем только первую стратегию для скорости
                new_tweets = await self.find_new_tweets(
                    username, max_check=self.max_tweets_per_account, strategy_index=0
                )

                if new_tweets:
                    all_candidates.extend(new_tweets)
                    print(f"✅ @{username}: найдено {len(new_tweets)} твитов")
                else:
                    print(f"😴 @{username}: новых твитов нет")

                # Небольшая пауза между аккаунтами
                await asyncio.sleep(1)

            except Exception as e:
                print(f"💥 Ошибка для @{username}: {e}")
                continue

        return all_candidates

    async def run_cycle(self):
        """ИСПРАВЛЕННОЕ выполнение одного цикла"""
        cycle_start = datetime.now()
        self.stats["total_cycles"] += 1

        print(f"\n🔄 ЦИКЛ #{self.stats['total_cycles']}")
        print(f"⏰ {cycle_start.strftime('%H:%M:%S')}")
        print("=" * 50)

        # Проверяем лимиты
        if not self.can_respond_today():
            print(f"🚫 Достигнут дневной лимит ({self.max_daily_responses} ответов)")
            return

        # Поиск по аккаунтам
        print(f"🔍 Начинаем поиск по {len(USERNAMES)} аккаунтам...")
        all_candidates = await self.smart_account_search()

        if not all_candidates:
            print("😴 Новых твитов не найдено")
            self.stats["search_efficiency"]["cycles_without_responses"] += 1
            return

        print(f"🎯 Найдено {len(all_candidates)} кандидатов для ответа")

        # Сортируем кандидатов по длине (длинные твиты приоритетнее)
        sorted_candidates = sorted(all_candidates, key=lambda x: -len(x["text"]))

        responses_this_cycle = 0

        # Обрабатываем кандидатов
        for tweet in sorted_candidates[: self.max_responses_per_cycle]:
            if responses_this_cycle >= self.max_responses_per_cycle:
                break

            try:
                print(f"\n🎯 Обрабатываем твит от @{tweet['username']}")
                print(f"📝 Текст: {tweet['text'][:100]}...")

                # Генерируем ответ
                response, style, confidence = await self.generate_response(
                    tweet["text"], tweet["username"]
                )

                if response and confidence >= self.min_confidence_threshold:
                    print(f"🎨 Стиль: {style}")
                    print(f"🎯 Уверенность: {confidence:.2f}")
                    print(f'💬 Ответ: "{response}"')

                    # Отправляем ответ
                    if await self.send_response_to_tweet(tweet, response):
                        print(f"✅ Ответ отправлен на @{tweet['username']}!")

                        # Обновляем статистику
                        self.mark_tweet_processed(tweet["id"])
                        self.stats["total_responses"] += 1
                        self.stats["responses_today"] += 1
                        self.stats["accounts_stats"][tweet["username"]][
                            "responded"
                        ] += 1
                        responses_this_cycle += 1

                        # Логируем ответ
                        self.log_response(tweet, response, style, confidence)

                    else:
                        print(f"❌ Ошибка отправки ответа")
                        self.mark_tweet_processed(tweet["id"])
                else:
                    print(
                        f"❌ Ответ не прошел проверку качества (уверенность: {confidence:.2f})"
                    )
                    self.mark_tweet_processed(tweet["id"])

            except Exception as e:
                print(f"💥 Ошибка обработки твита: {e}")
                continue

        # Обновляем статистику эффективности
        if responses_this_cycle > 0:
            self.stats["search_efficiency"]["cycles_with_responses"] += 1
        else:
            self.stats["search_efficiency"]["cycles_without_responses"] += 1

        # Сохраняем статистику
        self.save_stats()

        cycle_end = datetime.now()
        duration = (cycle_end - cycle_start).total_seconds()

        print(f"\n📊 Цикл завершен за {duration:.1f} сек")
        print(f"📤 Ответов в этом цикле: {responses_this_cycle}")
        print(
            f"📈 Всего ответов сегодня: {self.stats['responses_today']}/{self.max_daily_responses}"
        )
        print(f"🎯 Найдено кандидатов: {len(all_candidates)}")

    def log_response(self, tweet, response, style, confidence):
        """Логирование отправленного ответа"""
        try:
            response_log = {
                "timestamp": datetime.now().isoformat(),
                "username": tweet["username"],
                "tweet_id": tweet["id"],
                "tweet_text": tweet["text"][:1000],
                "response": response,
                "style": style,
                "confidence": confidence,
            }

            log_file = Path("responses_log.json")
            logs = []
            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                except:
                    pass

            logs.append(response_log)

            # Храним только последние 100 записей
            if len(logs) > 100:
                logs = logs[-100:]

            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ Ошибка логирования: {e}")

    async def cleanup(self):
        """ИСПРАВЛЕННАЯ очистка ресурсов"""
        try:
            print("🧹 Начинаем очистку ресурсов...")

            # Закрываем контекст браузера
            if self.browser_context:
                try:
                    await self.browser_context.close()
                    print("✅ Контекст браузера закрыт")
                except Exception as e:
                    print(f"⚠️ Ошибка закрытия контекста: {e}")
                finally:
                    self.browser_context = None

            # Останавливаем playwright
            if self.playwright:
                try:
                    await self.playwright.stop()
                    print("✅ Playwright остановлен")
                except Exception as e:
                    print(f"⚠️ Ошибка остановки playwright: {e}")
                finally:
                    self.playwright = None

            print("✅ Очистка завершена")

        except Exception as e:
            print(f"💥 Ошибка при очистке: {e}")

    async def run_forever(self):
        """Главный цикл работы"""
        print("🤖 ИСПРАВЛЕННЫЙ АВТОМАТИЧЕСКИЙ РЕЖИМ TWITTER ОТВЕТЧИКА")
        print("=" * 60)
        print(f"👀 Браузер: {'ВИДИМЫЙ' if self.show_browser else 'СКРЫТЫЙ'}")
        print(f"⏰ Интервал: {self.cycle_interval_minutes} минут")
        print(
            f"📊 Лимит: {self.max_responses_per_cycle} ответ за цикл, {self.max_daily_responses} в день"
        )
        print(f"👥 Мониторинг: {len(USERNAMES)} аккаунтов")
        print(f"🎯 Порог уверенности: {self.min_confidence_threshold}")
        print(f"🔄 Запуск: {datetime.now().strftime('%H:%M:%S')}")
        print()

        # Показываем список аккаунтов
        print("📋 Отслеживаемые аккаунты:")
        for i, username in enumerate(USERNAMES, 1):
            stats = self.stats["accounts_stats"].get(username, {})
            print(
                f"  {i:2d}. @{username} (проверено: {stats.get('checked', 0)}, ответов: {stats.get('responded', 0)})"
            )
        print()

        # Проверяем авторизацию
        print("🔐 Предварительная проверка авторизации...")
        if not await self.check_and_fix_auth():
            print("❌ Не удалось авторизоваться. Завершение работы.")
            return

        # Инициализация AI
        try:
            await self.get_reply_engine()
            print("✅ AI движок готов!")
        except Exception as e:
            print(f"❌ Ошибка AI: {e}")
            return

        try:
            while True:
                # Выполняем цикл
                await self.run_cycle()

                # Ждем до следующего цикла
                wait_seconds = self.cycle_interval_minutes * 60
                next_run = datetime.now() + timedelta(seconds=wait_seconds)

                print(f"\n⏱️ Следующий цикл в {next_run.strftime('%H:%M:%S')}")
                print(f"💤 Ожидание {self.cycle_interval_minutes} минут...")

                # Ждем с возможностью прерывания
                try:
                    await asyncio.sleep(wait_seconds)
                except KeyboardInterrupt:
                    break

        except KeyboardInterrupt:
            print("\n🛑 Остановлено пользователем")
        except Exception as e:
            print(f"\n💥 Критическая ошибка: {e}")
        finally:
            await self.cleanup()
            self.save_stats()
            self.save_history()
            print("💾 Данные сохранены")
            print("🏁 Автоответчик остановлен")

    def show_detailed_stats(self):
        """Показать детальную статистику"""
        print(f"\n📊 ДЕТАЛЬНАЯ СТАТИСТИКА")
        print("=" * 50)
        print(f"⏰ Запущен: {self.stats.get('start_time', 'N/A')}")
        print(f"🔄 Всего циклов: {self.stats['total_cycles']}")
        print(f"📤 Всего ответов: {self.stats['total_responses']}")
        print(
            f"📈 Ответов сегодня: {self.stats['responses_today']}/{self.max_daily_responses}"
        )
        print(f"📚 Обработано твитов: {len(self.processed_tweets)}")

        # Эффективность поиска
        search_stats = self.stats.get("search_efficiency", {})
        success_cycles = search_stats.get("cycles_with_responses", 0)
        fail_cycles = search_stats.get("cycles_without_responses", 0)
        total = success_cycles + fail_cycles

        if total > 0:
            success_rate = (success_cycles / total) * 100
            print(
                f"🎯 Эффективность поиска: {success_rate:.1f}% ({success_cycles}/{total})"
            )

        print(f"\n👥 СТАТИСТИКА ПО АККАУНТАМ:")
        print("-" * 50)

        # Сортируем аккаунты по количеству ответов
        sorted_accounts = sorted(
            self.stats["accounts_stats"].items(),
            key=lambda x: x[1].get("responded", 0),
            reverse=True,
        )

        for username, stats in sorted_accounts:
            checked = stats.get("checked", 0)
            responded = stats.get("responded", 0)
            found = stats.get("tweets_found", 0)

            response_rate = (responded / checked * 100) if checked > 0 else 0

            print(
                f"@{username:15} | Проверено: {checked:3d} | Найдено: {found:3d} | Ответов: {responded:2d} | Rate: {response_rate:4.1f}%"
            )

    async def test_single_account(self, username):
        """Тестирование поиска для одного аккаунта"""
        print(f"\n🧪 ТЕСТ ПОИСКА ДЛЯ @{username}")
        print("=" * 40)

        if username not in USERNAMES:
            print(f"❌ Аккаунт @{username} не в списке мониторинга")
            return

        try:
            # Проверяем авторизацию
            if not await self.check_and_fix_auth():
                print("❌ Не авторизован")
                return

            # Инициализируем AI
            await self.get_reply_engine()

            print(f"🔍 Ищем твиты...")
            tweets = await self.find_new_tweets(username, max_check=5, strategy_index=0)

            if tweets:
                print(f"✅ Найдено {len(tweets)} твитов:")
                for i, tweet in enumerate(tweets[:3], 1):
                    print(f"\n  {i}. {tweet['text'][:80]}...")

                    # Тестируем генерацию ответа
                    response, style, confidence = await self.generate_response(
                        tweet["text"], username
                    )
                    if response:
                        print(f"     🎨 Стиль: {style}")
                        print(f"     🎯 Уверенность: {confidence:.2f}")
                        print(f"     💬 Ответ: {response[:60]}...")
                    else:
                        print(f"     ❌ Не удалось сгенерировать ответ")
            else:
                print("❌ Новые твиты не найдены")

        except Exception as e:
            print(f"💥 Ошибка тестирования: {e}")
        finally:
            await self.cleanup()


def main():
    """Точка входа"""
    responder = AutoCycleResponder()

    print("🤖 Исправленный Twitter ответчик")
    print("=" * 40)
    print("1. Запустить автоматический режим")
    print("2. Показать детальную статистику")
    print("3. Тестировать поиск для аккаунта")
    print("4. Очистить историю")
    print("5. Настройки")
    print("0. Выход")

    choice = input("\nВыберите [0-5]: ").strip()

    if choice == "1":
        print(
            f"\n⚠️ ВНИМАНИЕ: Запуск в {'DRY RUN' if responder.dry_run else 'LIVE'} режиме!"
        )
        print(
            f"Бот будет автоматически отвечать на твиты каждые {responder.cycle_interval_minutes} минут"
        )
        print(f"Отслеживается {len(USERNAMES)} аккаунтов")
        confirm = input("Продолжить? [y/N]: ").strip().lower()

        if confirm == "y":
            try:
                asyncio.run(responder.run_forever())
            except KeyboardInterrupt:
                print("\n🛑 Остановлено пользователем")
        else:
            print("❌ Отменено")

    elif choice == "2":
        responder.show_detailed_stats()

    elif choice == "3":
        print(f"\nДоступные аккаунты:")
        for i, username in enumerate(USERNAMES, 1):
            print(f"  {i}. @{username}")

        try:
            idx = int(input("Выберите номер аккаунта: ")) - 1
            if 0 <= idx < len(USERNAMES):
                try:
                    asyncio.run(responder.test_single_account(USERNAMES[idx]))
                except KeyboardInterrupt:
                    print("\n🛑 Тест прерван")
            else:
                print("❌ Неверный номер")
        except ValueError:
            print("❌ Введите число")

    elif choice == "4":
        confirm = (
            input("Очистить всю историю обработанных твитов? [y/N]: ").strip().lower()
        )
        if confirm == "y":
            responder.processed_tweets.clear()
            responder.save_history()
            print("✅ История очищена")

    elif choice == "5":
        print(f"\n⚙️ ТЕКУЩИЕ НАСТРОЙКИ:")
        print(f"   Интервал циклов: {responder.cycle_interval_minutes} мин")
        print(f"   Ответов за цикл: {responder.max_responses_per_cycle}")
        print(f"   Ответов в день: {responder.max_daily_responses}")
        print(f"   Порог уверенности: {responder.min_confidence_threshold}")
        print(f"   Твитов на аккаунт: {responder.max_tweets_per_account}")
        print(
            f"   Режим браузера: {'ВИДИМЫЙ' if responder.show_browser else 'СКРЫТЫЙ'}"
        )
        print(f"   Сухой прогон: {'ДА' if responder.dry_run else 'НЕТ'}")

        print(f"\nИзменить настройки:")
        print(f"1. Интервал (текущий: {responder.cycle_interval_minutes} мин)")
        print(f"2. Лимит за цикл (текущий: {responder.max_responses_per_cycle})")
        print(f"3. Дневной лимит (текущий: {responder.max_daily_responses})")
        print(f"4. Порог уверенности (текущий: {responder.min_confidence_threshold})")
        print(f"5. Включить/выключить сухой прогон")
        print(f"6. Показать/скрыть браузер")

        setting = input("Что изменить? [1-6]: ").strip()

        if setting == "1":
            try:
                new_interval = int(input("Новый интервал (минуты): "))
                if 5 <= new_interval <= 120:
                    responder.cycle_interval_minutes = new_interval
                    print(f"✅ Интервал изменен на {new_interval} минут")
                else:
                    print("❌ Интервал должен быть от 5 до 120 минут")
            except ValueError:
                print("❌ Введите число")

        elif setting == "2":
            try:
                new_limit = int(input("Новый лимит за цикл: "))
                if 1 <= new_limit <= 5:
                    responder.max_responses_per_cycle = new_limit
                    print(f"✅ Лимит изменен на {new_limit}")
                else:
                    print("❌ Лимит должен быть от 1 до 5")
            except ValueError:
                print("❌ Введите число")

        elif setting == "3":
            try:
                new_daily = int(input("Новый дневной лимит: "))
                if 5 <= new_daily <= 50:
                    responder.max_daily_responses = new_daily
                    print(f"✅ Дневной лимит изменен на {new_daily}")
                else:
                    print("❌ Дневной лимит должен быть от 5 до 50")
            except ValueError:
                print("❌ Введите число")

        elif setting == "4":
            try:
                new_threshold = float(input("Новый порог уверенности (0.1-1.0): "))
                if 0.1 <= new_threshold <= 1.0:
                    responder.min_confidence_threshold = new_threshold
                    print(f"✅ Порог изменен на {new_threshold}")
                else:
                    print("❌ Порог должен быть от 0.1 до 1.0")
            except ValueError:
                print("❌ Введите число")

        elif setting == "5":
            responder.dry_run = not responder.dry_run
            print(f"✅ Сухой прогон: {'ВКЛЮЧЕН' if responder.dry_run else 'ВЫКЛЮЧЕН'}")

        elif setting == "6":
            responder.show_browser = not responder.show_browser
            print(f"✅ Браузер: {'ВИДИМЫЙ' if responder.show_browser else 'СКРЫТЫЙ'}")

    elif choice == "0":
        print("👋 До свидания!")

    else:
        print("❌ Неверный выбор")


if __name__ == "__main__":
    main()
