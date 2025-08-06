"""
DEVINVESTCOIN Conversion Optimizer
Умные хуки, психологические триггеры и CTA для максимальной конверсии
"""

import random
from typing import Dict, List, Tuple
from datetime import datetime


class ConversionOptimizer:
    """Оптимизатор конверсии для увеличения переходов в профиль"""

    def __init__(self):
        # Психологические триггеры
        self.psychological_triggers = {
            "fomo": {
                "phrases": [
                    "last ones to know usually pay the most",
                    "early ones eating, late ones feeding",
                    "some build the future, others buy it at 100x",
                    "builders get tokens, watchers get receipts",
                    "those who ship together, profit together",
                ],
                "weight": 0.3,
            },
            "curiosity": {
                "phrases": [
                    "found the pattern nobody's talking about",
                    "there's a reason smart money is quiet right now",
                    "what if memes were just the beginning?",
                    "the real alpha isn't where you think",
                    "connecting dots others don't see yet",
                ],
                "weight": 0.25,
            },
            "authority": {
                "phrases": [
                    "shipped 3 protocols, rugged by 0",
                    "built through 2 bears, still here",
                    "code commits > price predictions",
                    "we called the last 3 moves correctly",
                    "devs know what's really shipping",
                ],
                "weight": 0.2,
            },
            "social_proof": {
                "phrases": [
                    "devs already know what's happening",
                    "builders circle getting bigger",
                    "smart ones already positioning",
                    "the shift already started",
                    "early community eating good",
                ],
                "weight": 0.15,
            },
            "scarcity": {
                "phrases": [
                    "not everyone gets it yet",
                    "few understand this",
                    "only builders see it coming",
                    "limited time to position",
                    "window closing faster than expected",
                ],
                "weight": 0.1,
            },
        }

        # CTA варианты (subtle but effective)
        self.cta_templates = {
            "soft": [
                "👀 @DevInvestCoin",
                "cooking → @DevInvestCoin",
                "real ones → @DevInvestCoin",
                "builders → @DevInvestCoin",
                "if ykyk → @DevInvestCoin",
            ],
            "medium": [
                "we're building it different → @DevInvestCoin",
                "devs + degens united → @DevInvestCoin",
                "shipping daily → @DevInvestCoin",
                "where builders meet bags → @DevInvestCoin",
                "memecoin with commits → @DevInvestCoin",
            ],
            "strong": [
                "stop watching, start building → @DevInvestCoin",
                "builders eat first → @DevInvestCoin",
                "your last chance to be early → @DevInvestCoin",
                "this ages well → @DevInvestCoin",
                "screenshot this → @DevInvestCoin",
            ],
        }

        # Контекстные усилители
        self.context_amplifiers = {
            "bear_market": ["still building", "bear market builders", "survived worse"],
            "bull_market": ["everyone's a genius now", "top signal", "euphoria phase"],
            "technical": [
                "on-chain doesn't lie",
                "code > hopium",
                "trustless > trusted",
            ],
            "meme": [
                "memes are liquidity",
                "culture eats strategy",
                "vibes > fundamentals",
            ],
            "fud": ["fud = opportunity", "they'll fomo at 10x", "doubt feeds builders"],
        }

        # Эмоциональные якоря
        self.emotional_anchors = {
            "pain": ["tired of rugs?", "exit liquidity again?", "another L?"],
            "gain": ["builders always win", "early = wealthy", "this prints different"],
            "fear": [
                "ngmi without code",
                "last cycle before AI takes over",
                "priced out forever",
            ],
            "pride": [
                "real builders know",
                "you get it or you don't",
                "not for tourists",
            ],
        }

        # История конверсий для обучения
        self.conversion_history = []
        self.ab_test_results = {}

    def optimize_reply(
        self, original_reply: str, tweet_context: Dict, aggressiveness: str = "medium"
    ) -> Tuple[str, Dict]:
        """
        Оптимизирует ответ для максимальной конверсии

        Args:
            original_reply: Исходный ответ от AI
            tweet_context: Контекст твита (автор, тема, sentiment)
            aggressiveness: Уровень агрессивности CTA (soft/medium/strong)

        Returns:
            Tuple[оптимизированный ответ, метрики]
        """

        # Анализируем контекст
        author = tweet_context.get("username", "")
        tweet_text = tweet_context.get("text", "").lower()
        sentiment = self._detect_sentiment(tweet_text)
        topic = self._detect_topic(tweet_text)

        # Выбираем стратегию
        strategy = self._select_strategy(author, sentiment, topic)

        # Добавляем психологический триггер
        trigger = self._select_trigger(strategy, sentiment)

        # Формируем хук
        hook = self._create_hook(original_reply, trigger, topic)

        # Добавляем CTA
        cta = self._select_cta(aggressiveness, sentiment)

        # Собираем финальный ответ
        optimized = self._assemble_reply(hook, cta, original_reply)

        # Проверяем длину
        if len(optimized) > 280:
            optimized = self._compress_reply(optimized, cta)

        # Метрики для отслеживания
        metrics = {
            "strategy": strategy,
            "trigger_type": trigger["type"] if trigger else None,
            "cta_level": aggressiveness,
            "sentiment": sentiment,
            "topic": topic,
            "original_length": len(original_reply),
            "optimized_length": len(optimized),
            "timestamp": datetime.now().isoformat(),
        }

        return optimized, metrics

    def _detect_sentiment(self, text: str) -> str:
        """Определяет настроение твита"""
        bearish_words = ["crash", "dump", "rug", "scam", "dead", "over", "bear"]
        bullish_words = ["moon", "pump", "bull", "ath", "rocket", "green", "gm"]
        neutral_words = ["building", "shipping", "coding", "launching"]

        text_lower = text.lower()

        bearish_score = sum(1 for word in bearish_words if word in text_lower)
        bullish_score = sum(1 for word in bullish_words if word in text_lower)
        neutral_score = sum(1 for word in neutral_words if word in text_lower)

        if bearish_score > bullish_score and bearish_score > neutral_score:
            return "bearish"
        elif bullish_score > bearish_score and bullish_score > neutral_score:
            return "bullish"
        else:
            return "neutral"

    def _detect_topic(self, text: str) -> str:
        """Определяет тему твита"""
        topics = {
            "technical": [
                "protocol",
                "smart contract",
                "blockchain",
                "consensus",
                "zkp",
            ],
            "trading": ["price", "chart", "resistance", "support", "volume"],
            "meme": ["wagmi", "ngmi", "gm", "fren", "ser", "probably nothing"],
            "building": ["shipping", "building", "launching", "deployed", "mainnet"],
            "fud": ["scam", "rug", "ponzi", "fake", "warning"],
        }

        text_lower = text.lower()
        topic_scores = {}

        for topic, keywords in topics.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score

        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        return "general"

    def _select_strategy(self, author: str, sentiment: str, topic: str) -> str:
        """Выбирает стратегию ответа"""
        # VIP авторы - максимальная персонализация
        vip_authors = ["vitalikbuterin", "elonmusk", "cz_binance", "sassal0x"]
        if author.lower() in vip_authors:
            return "authority"

        # По теме и настроению
        if sentiment == "bearish":
            return "fomo"  # Используем страх упущенной выгоды
        elif sentiment == "bullish":
            return "social_proof"  # Подтверждаем и усиливаем
        elif topic == "building":
            return "authority"  # Показываем экспертность
        elif topic == "meme":
            return "curiosity"  # Интригуем
        else:
            return "curiosity"  # По умолчанию - любопытство

    def _select_trigger(self, strategy: str, sentiment: str) -> Dict:
        """Выбирает психологический триггер"""
        if strategy in self.psychological_triggers:
            phrases = self.psychological_triggers[strategy]["phrases"]
            selected_phrase = random.choice(phrases)

            return {
                "type": strategy,
                "phrase": selected_phrase,
                "weight": self.psychological_triggers[strategy]["weight"],
            }
        return None

    def _create_hook(self, original: str, trigger: Dict, topic: str) -> str:
        """Создает зацепку в начале ответа"""
        if not trigger:
            return original

        # Добавляем контекстный усилитель
        amplifier = ""
        if topic in self.context_amplifiers:
            amplifier = random.choice(self.context_amplifiers[topic])

        # Формируем хук
        if amplifier:
            hook = f"{trigger['phrase']}. {amplifier}."
        else:
            hook = trigger["phrase"]

        return hook

    def _select_cta(self, level: str, sentiment: str) -> str:
        """Выбирает призыв к действию"""
        if level in self.cta_templates:
            options = self.cta_templates[level]

            # Адаптируем под настроение
            if sentiment == "bearish" and level == "strong":
                # Более агрессивный CTA для медвежьего рынка
                return random.choice(self.cta_templates["strong"])
            elif sentiment == "bullish" and level == "soft":
                # Мягче для бычьего рынка
                return random.choice(self.cta_templates["soft"])

            return random.choice(options)

        return "→ @DevInvestCoin"

    def _assemble_reply(self, hook: str, cta: str, original: str) -> str:
        """Собирает финальный ответ"""
        # Варианты сборки
        templates = [
            f"{hook} {cta}",
            f"{hook}\n\n{cta}",
            (
                f"{original[:100]}... {cta}"
                if len(original) > 100
                else f"{original} {cta}"
            ),
        ]

        # Выбираем лучший вариант по длине
        valid_templates = [t for t in templates if len(t) <= 280]

        if valid_templates:
            return random.choice(valid_templates)

        # Fallback
        return f"{hook[:200]} {cta}"

    def _compress_reply(self, reply: str, cta: str) -> str:
        """Сжимает ответ до 280 символов"""
        if len(reply) <= 280:
            return reply

        # Оставляем место для CTA
        max_length = 280 - len(cta) - 3  # 3 символа на "..."

        # Обрезаем и добавляем CTA
        compressed = reply[:max_length] + "... " + cta

        return compressed

    def track_conversion(self, reply_id: str, converted: bool, metrics: Dict):
        """Отслеживает конверсию для обучения"""
        self.conversion_history.append(
            {
                "reply_id": reply_id,
                "converted": converted,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Обновляем A/B тест результаты
        strategy = metrics.get("strategy")
        if strategy not in self.ab_test_results:
            self.ab_test_results[strategy] = {"attempts": 0, "conversions": 0}

        self.ab_test_results[strategy]["attempts"] += 1
        if converted:
            self.ab_test_results[strategy]["conversions"] += 1

    def get_best_strategies(self) -> List[Tuple[str, float]]:
        """Возвращает лучшие стратегии по конверсии"""
        results = []
        for strategy, data in self.ab_test_results.items():
            if data["attempts"] > 0:
                conversion_rate = data["conversions"] / data["attempts"]
                results.append((strategy, conversion_rate))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def generate_viral_reply(self, tweet_text: str) -> str:
        """Генерирует потенциально вирусный ответ"""
        viral_templates = [
            "this is why {insight}. few.",
            "imagine not {action} in 2024",
            "ser, {observation}. respectfully.",
            "{statement}. that's it. that's the tweet.",
            "gm to everyone except {exception}",
            "{hot_take}. i said what i said.",
            "normalize {behavior}",
            "a thread on why {topic} is actually {unexpected}: 🧵",
            "{question}? asking for a fren",
            "POV: {scenario}",
            "breaking: {fake_news}. jk but {real_insight}",
            "{statement}. no i will not elaborate.",
            "RT if you {action}. like if you {opposite_action}.",
            "{observation}. probably nothing.",
            "anon, {advice}",
        ]

        # Анализируем твит для контекста
        sentiment = self._detect_sentiment(tweet_text)
        topic = self._detect_topic(tweet_text)

        # Генерируем инсайты на основе контекста
        insights = {
            "bearish": "bears become exit liquidity",
            "bullish": "tops are just higher bottoms",
            "neutral": "builders keep building",
            "technical": "code doesn't care about price",
            "meme": "memes are the real fundamentals",
        }

        # Выбираем шаблон и заполняем
        template = random.choice(viral_templates)

        # Примеры заполнения (можно расширить)
        replacements = {
            "{insight}": insights.get(sentiment, "ngmi thinking small"),
            "{action}": "building through the bear",
            "{observation}": "your favorite influencer can't code",
            "{statement}": "memecoins saved crypto",
            "{exception}": "people who sold the bottom",
            "{hot_take}": "DAOs work better than companies",
            "{behavior}": "shipping before shilling",
            "{topic}": "DeFi",
            "{unexpected}": "based",
            "{question}": "who's still building",
            "{scenario}": "you're early but everyone says you're late",
            "{fake_news}": "bitcoin CEO just quit",
            "{real_insight}": "we're all gonna make it",
            "{advice}": "touch code not grass",
            "{opposite_action}": "still watching",
        }

        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)

        # Добавляем subtle CTA
        if random.random() > 0.7:  # 30% шанс
            template += f"\n\n@DevInvestCoin"

        return template


# Интеграция с основным движком
class EnhancedReplyEngine:
    """Расширенный движок с оптимизацией конверсии"""

    def __init__(self, base_engine, optimizer):
        self.base_engine = base_engine
        self.optimizer = optimizer
        self.viral_mode_threshold = 10000  # Followers для viral mode

    async def generate_optimized_reply(
        self, tweet_text: str, username: str, followers_count: int = 0
    ) -> Dict:
        """Генерирует оптимизированный ответ"""

        # Получаем базовый ответ
        base_result = await self.base_engine.generate_reply(tweet_text)

        # Определяем уровень агрессивности CTA
        if followers_count > self.viral_mode_threshold:
            # Для больших аккаунтов - вирусный режим
            optimized_reply = self.optimizer.generate_viral_reply(tweet_text)
            strategy = "viral"
        else:
            # Обычная оптимизация
            aggressiveness = self._determine_aggressiveness(followers_count)

            tweet_context = {
                "username": username,
                "text": tweet_text,
                "followers": followers_count,
            }

            optimized_reply, metrics = self.optimizer.optimize_reply(
                base_result["reply"], tweet_context, aggressiveness
            )
            strategy = metrics.get("strategy", "unknown")

        return {
            "reply": optimized_reply,
            "original_reply": base_result["reply"],
            "strategy": strategy,
            "confidence_score": base_result.get("confidence_score", 0.8),
            "optimized": True,
        }

    def _determine_aggressiveness(self, followers: int) -> str:
        """Определяет уровень агрессивности CTA"""
        if followers < 1000:
            return "strong"  # Маленькие аккаунты - сильный CTA
        elif followers < 10000:
            return "medium"  # Средние - умеренный
        else:
            return "soft"  # Большие - мягкий


# Тестирование
if __name__ == "__main__":
    import asyncio

    # Инициализация
    optimizer = ConversionOptimizer()

    # Тестовые твиты
    test_tweets = [
        {
            "text": "Bitcoin dumping again, we're all gonna die",
            "username": "crypto_whale",
            "followers": 50000,
        },
        {
            "text": "Just deployed my new DeFi protocol on mainnet!",
            "username": "anon_dev",
            "followers": 500,
        },
        {
            "text": "GM builders, what are we shipping today?",
            "username": "builder_dao",
            "followers": 5000,
        },
    ]

    print("🎯 CONVERSION OPTIMIZER TEST")
    print("=" * 50)

    for tweet in test_tweets:
        print(f"\n📝 Original tweet from @{tweet['username']}:")
        print(f"   '{tweet['text']}'")
        print(f"   Followers: {tweet['followers']:,}")

        # Тест обычной оптимизации
        original_reply = "That's an interesting perspective on the market"

        context = {
            "username": tweet["username"],
            "text": tweet["text"],
            "followers": tweet["followers"],
        }

        optimized, metrics = optimizer.optimize_reply(original_reply, context, "medium")

        print(f"\n💬 Optimized reply:")
        print(f"   '{optimized}'")
        print(f"   Strategy: {metrics['strategy']}")
        print(f"   Length: {metrics['optimized_length']}/280")

        # Тест вирусного ответа
        viral = optimizer.generate_viral_reply(tweet["text"])
        print(f"\n🔥 Viral reply:")
        print(f"   '{viral}'")

        print("-" * 50)

    # Показываем лучшие стратегии
    print("\n📊 A/B Test Results:")
    for strategy, rate in optimizer.get_best_strategies():
        print(f"   {strategy}: {rate:.1%} conversion rate")
