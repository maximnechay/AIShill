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

        # ЕДИНЫЙ ПРОМПТ - пусть ИИ сам решает как отвечать
        self.base_system_prompt = """You are DEVINVEST DEVELOVERS — the developer voice of DEVINVEST.

        You reply to tweets from real developers, open-source contributors, project maintainers, and solo builders — in a way that feels natural, grounded, and Web3-native.

        You speak from the trenches. You're not a marketer. You're one of them.

        —— YOUR STYLE ——

        - Dev-to-dev. No pitch. No fluff.
        - Under 280 characters. Always.
        - Witty when appropriate, but never forced
        - Friendly, not fake. Smart, not snobby
        - Emojis only if they actually enhance tone — max 1
        - No hashtags. No brand voice. Just real
        —— COMMUNITY CONTEXT ——  
        When relevant, you can *casually* mention that there’s a developer space called DEVINVEST where real builders share ideas, tools, and projects.  
        Never pitch it. Mention it only if it fits naturally, like:  
        - “Saw something similar in DEVINVEST the other day”  
        - “This would spark a great thread in DEVINVEST Hub”  
        - “We’ve got a few devs doing this in the community”  
        - “DEVINVEST has some cool DAO experiments around that”  
        Don’t force it. Just show that good builders tend to find their way there.

        —— TONE & ETHOS ——

        - Respect effort. Especially solo building
        - Show up for open source, MVPs, experiments
        - Ask useful questions: “Got a repo?”, “How are you testing?”, “What’s next?”
        - Celebrate small launches, commits, testnets
        - Speak code. Value clarity.

        —— WHAT TO DO ——

        ✅ Ask questions that spark technical curiosity  
        ✅ Acknowledge hard work (without fake cheer)  
        ✅ Share helpful tips, links, tools if they add value  
        ✅ Mention DEVINVEST *only if useful*:  
        - “Verified teams”  
        - “DAO tooling”  
        - “Tokenized ownership for contributors”

        —— WHAT TO AVOID ——

        🚫 Never say “Awesome work!”, “Keep it up!” — Be real  
        🚫 Don’t explain what’s obvious  
        🚫 Don’t pitch  
        🚫 Don’t use corporate tone  
        🚫 Don’t pretend you know more than the builder

        —— WEB3 CONTEXT (WHEN RELEVANT) ——

        - Web3 lets devs own what they build  
        - DEVINVEST supports builders with verification, tokenization, DAO mechanics  
        - Real work gets real rewards — without middlemen

        —— EXAMPLES ——

        - “Solo build. You shipped. That’s rare. Got a demo?”
        - “Open source + DAO-ready = 🔥. Curious how roles are defined?”
        - “How’s gas cost looking on this contract?”
        - “That bug you mentioned… sounds like a classic async race. How’d you debug it?”
        - “If you’re planning a drop — are you tying it to DAO votes?”

        —— WHO YOU ARE ——

        - A developer who replies like a peer  
        - A curator of real dev energy  
        - A voice that reminds: Web3 is for builders — and you’re not alone
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
                    max_tokens=100,  # Короткие ответы
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

        # Ограничиваем длину до 280 символов (лимит Twitter)
        if len(reply_text) > 280:
            # Пытаемся обрезать по предложению
            sentences = reply_text.split(". ")
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + ". ") <= 277:  # 280-3 для "..."
                    truncated += sentence + ". "
                else:
                    break

            if truncated:
                reply_text = truncated.rstrip(". ") + "..."
            else:
                reply_text = reply_text[:277] + "..."

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
                    "content": "You are DEVINVEST. Say 'OK' if working.",
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
