import asyncio
import time
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from openai import AsyncOpenAI
import json
import re
from dataclasses import dataclass, field
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class ReplyStats:
    """Statistics tracking for the reply engine"""

    total_requests: int = 0
    total_replies_generated: int = 0
    total_tokens_used: int = 0
    total_processing_time: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    error_count: int = 0


class Settings:
    """Simple settings class if config module not available"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")


class ReplyEngine:
    """AI-powered reply generation engine - SIMPLIFIED VERSION"""

    def __init__(self):
        try:
            from config import get_settings

            self.settings = get_settings()
        except ImportError:
            self.settings = Settings()

        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.stats = ReplyStats()
        self.base_system_prompt = """You are XinvestAI — an AI-powered cryptocurrency intelligence platform.

        —— WHO YOU ARE ——

        - XinvestAI analyzes crypto influencer tweets in real-time for trading signals
        - You provide intelligent market insights based on social sentiment analysis  
        - You track 50+ crypto influencers including Elon Musk, CZ, Vitalik, Michael Saylor
        - You deliver instant notifications about market-moving tweets to traders
        - You believe smart trading requires both technical analysis AND social intelligence

        —— PERSONALITY ——

        - Sharp. Data-driven. Professional
        - Confident but not overhyped
        - You speak like a seasoned trader who values edge over noise
        - You care about profitable signals — not just community vibes
        - You're focused on actionable intelligence

        —— WHEN TO MENTION XinvestAI ——

        - When discussing crypto market analysis or trading signals
        - If someone asks about tweet analysis or social sentiment
        - When topics involve crypto influencers or their market impact

        → Examples:
        - This is exactly what XinvestAI tracks — sentiment shifts from major influencers
        - We analyze tweets like this in real-time for our subscribers  
        - XinvestAI caught this signal 3 minutes after the tweet

        —— PLATFORM CONTEXT ——

        When relevant, mention XinvestAI capabilities:

        - Real-time analysis of crypto influencer tweets
        - AI-powered sentiment analysis with 95% accuracy
        - Instant Telegram notifications for subscribers
        - Coverage of Bitcoin, Ethereum, Solana, Dogecoin markets
        - Historical pattern recognition for price predictions

        Only mention features when they add value to the conversation.

        —— HOW YOU RESPOND ——

        - Replies should be under 280 characters
        - Professional but engaging tone
        - No excessive emojis or hype language
        - Focus on trading value and market intelligence
        - Share insights that help traders make better decisions

        —— TONE & VOICE ——

        - Professional trader mindset
        - Data-driven and analytical  
        - Confident in market knowledge
        - Helpful to serious crypto traders
        - No moon-boy language or false promises

        —— NEVER SAY ——

        - "To the moon", "HODL", "Diamond hands", "This is not financial advice"
        - No prediction of specific prices
        - No guarantee of profits
        - Don't oversell or sound like spam

        —— EXAMPLES ——

        - Tweet sentiment analysis shows strong bullish momentum — worth monitoring
        - This pattern historically precedes 15-20% moves within 48h
        - XinvestAI flagged similar signals from this account 3 times this month
        - Smart money follows social sentiment shifts — this is a clear signal
        - Real-time analysis beats delayed reactions in crypto markets

        —— WHY YOU EXIST ——

        You help serious crypto traders gain edge through social sentiment intelligence.
        You turn social media noise into actionable trading signals.
        You believe successful trading requires both technical AND social analysis.

        Professional trading intelligence. Not just hype tracking.
        """

    async def generate_reply(
        self,
        tweet_text: str,
        style: str = "auto",  # Игнорируем стиль - пусть ИИ решает
        language: str = "English",
        audience: Optional[str] = None,
        tone: Optional[str] = None,
        reply_length: str = "short",
        custom_instructions: Optional[str] = None,
    ) -> Dict:
        """Generate a reply using AI's natural understanding"""

        start_time = time.time()
        self.stats.total_requests += 1

        try:
            # Validate input
            tweet_text = tweet_text.strip()
            if len(tweet_text) < 1:
                raise ValueError("Tweet text cannot be empty")

            # Строим простой промпт
            system_prompt = self.base_system_prompt

            # Добавляем контекст аудитории если нужно
            if audience:
                audience_context = {
                    "crypto": "You're talking to crypto-native people who understand the space.",
                    "mainstream": "You're talking to people who might be new to crypto.",
                    "technical": "You're talking to developers and technical builders.",
                }
                if audience in audience_context:
                    system_prompt += f"\n\nCONTEXT: {audience_context[audience]}"

            # Добавляем дополнительные инструкции если есть
            if custom_instructions:
                system_prompt += f"\n\nADDITIONAL: {custom_instructions}"

            # Простой промпт для пользователя
            user_prompt = f'Respond to this tweet: "{tweet_text}"'

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # Вызываем OpenAI
            reply_text, tokens_used = await self._call_openai_with_retry(messages)

            # Простая постобработка
            reply_text = self._clean_reply(reply_text)

            # Считаем метрики
            processing_time = time.time() - start_time
            confidence_score = self._simple_confidence_check(reply_text, tweet_text)

            # Обновляем статистику
            self.stats.total_replies_generated += 1
            self.stats.total_tokens_used += tokens_used
            self.stats.total_processing_time += processing_time

            logger.info(
                f"Generated reply in {processing_time:.2f}s using {tokens_used} tokens"
            )

            return {
                "reply": reply_text,
                "style_used": "auto",
                "tone_used": "natural",
                "language_used": language,
                "confidence_score": confidence_score,
                "processing_time": processing_time,
                "tokens_used": tokens_used,
            }

        except Exception as e:
            self.stats.error_count += 1
            processing_time = time.time() - start_time
            logger.error(
                f"Error generating reply: {str(e)} (took {processing_time:.2f}s)"
            )
            raise

    async def _call_openai_with_retry(
        self, messages: List[Dict], max_retries: int = 3
    ) -> tuple[str, int]:
        """Call OpenAI API with retry logic"""

        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=messages,
                    temperature=0.7,  # Фиксированная температура - пусть ИИ сам регулирует тон
                    max_tokens=240,  # Короткие ответы
                    timeout=30.0,
                )

                reply_text = response.choices[0].message.content.strip()
                tokens_used = response.usage.total_tokens if response.usage else 0

                if not reply_text:
                    raise ValueError("Empty response from OpenAI")

                return reply_text, tokens_used

            except Exception as e:
                if attempt == max_retries - 1:
                    raise e

                wait_time = (2**attempt) + 1
                logger.warning(
                    f"API call failed (attempt {attempt + 1}), retrying in {wait_time}s: {str(e)}"
                )
                await asyncio.sleep(wait_time)

        raise Exception("Max retries exceeded")

    def _clean_reply(self, reply_text: str) -> str:
        """Simple reply cleanup"""

        # Убираем кавычки если ИИ обернул ответ
        reply_text = re.sub(r'^["\'](.+)["\']$', r"\1", reply_text.strip())

        # Убираем префиксы типа "Reply:" если есть
        reply_text = re.sub(
            r"^(Reply|Response):\s*", "", reply_text, flags=re.IGNORECASE
        )

        return reply_text.strip()

    def _simple_confidence_check(self, reply_text: str, original_tweet: str) -> float:
        """Simple confidence scoring"""

        score = 0.8  # Базовый высокий скор - доверяем ИИ

        # Проверяем длину
        if 10 <= len(reply_text) <= 280:
            score += 0.1
        else:
            score -= 0.2

        # Проверяем что это не слишком общий ответ
        generic_responses = [
            "interesting",
            "good point",
            "thanks for sharing",
            "i agree",
            "nice",
            "cool",
            "great",
        ]

        if any(generic in reply_text.lower() for generic in generic_responses):
            score -= 0.1

        # Проверяем что есть хоть какая-то связь с оригинальным твитом
        original_words = set(original_tweet.lower().split())
        reply_words = set(reply_text.lower().split())

        common_words = original_words.intersection(reply_words)
        if len(common_words) > 0:
            score += 0.1

        return max(0.1, min(1.0, score))

    async def get_statistics(self) -> Dict:
        """Get simple statistics"""
        uptime = datetime.now() - self.stats.start_time
        uptime_seconds = uptime.total_seconds()

        return {
            "total_requests": self.stats.total_requests,
            "total_replies_generated": self.stats.total_replies_generated,
            "total_tokens_used": self.stats.total_tokens_used,
            "average_processing_time": round(
                (
                    self.stats.total_processing_time / self.stats.total_requests
                    if self.stats.total_requests > 0
                    else 0
                ),
                3,
            ),
            "success_rate": round(
                (
                    (self.stats.total_requests - self.stats.error_count)
                    / self.stats.total_requests
                    * 100
                    if self.stats.total_requests > 0
                    else 0
                ),
                2,
            ),
            "uptime_formatted": str(uptime).split(".")[0],
        }

    async def health_check(self) -> Dict:
        """Simple health check"""
        try:
            test_messages = [
                {
                    "role": "system",
                    "content": "You are XinvestAI. Say 'OK' if working.",
                },
                {"role": "user", "content": "Test"},
            ]

            start_time = time.time()
            response = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=test_messages,
                max_tokens=10,
                timeout=10.0,
            )
            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "api_responsive": True,
                "api_response_time": round(response_time, 3),
                "model": self.settings.openai_model,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "api_responsive": False,
                "error": str(e),
                "model": self.settings.openai_model,
            }


# Test function
async def test_reply_engine():
    """Test the simplified reply engine"""
    print("🧪 Testing Simplified Reply Engine...")

    try:
        engine = ReplyEngine()

        test_tweets = [
            "Bitcoin is dead. Again.",
            "Building a new DeFi protocol with revolutionary tokenomics!",
            "GM builders! What are you shipping today?",
            "Just aped into another memecoin 🚀",
            "The future is decentralized",
        ]

        for tweet in test_tweets:
            result = await engine.generate_reply(tweet_text=tweet)
            print(f"\nTweet: {tweet}")
            print(f"Reply: {result['reply']}")
            print(f"Confidence: {result['confidence_score']:.2f}")
            print("-" * 50)

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_reply_engine())
