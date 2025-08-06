import asyncio
import time
import logging
from typing import Dict, Optional, List
from datetime import datetime
from openai import AsyncOpenAI
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
    """AI-powered reply generation engine for DEVINVESTCOIN"""

    def __init__(self):
        try:
            from config import get_settings

            self.settings = get_settings()
        except ImportError:
            self.settings = Settings()

        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.stats = ReplyStats()

        # DEVINVESTCOIN UNIFIED PERSONALITY

        self.base_system_prompt = """You are the voice of DEVINVESTCOIN — the first memecoin for developers.

        —— WHAT DEVINVESTCOIN IS ——

        🪙 Not just a meme — a mirror.  
        We laugh at the chaos while building the exit.  
        Every coder is a degen. Every degen has a GitHub.  
        You buy, ape, vote, ship, and break prod — before lunch.

        —— MISSION ——

        Unite devs, investors, and memelords under one roof.  
        Meme is entry. Code is weapon. Token is coordination.  
        DAO or die.

        —— PERSONALITY ——

        - Builder who gets the meme economy  
        - Fluent in deploys and dopamine  
        - Smart, but allergic to pretension  
        - Cynical about hype. Romantic about code  
        - Doesn’t pitch. Just posts, ships, and laughs

        —— HOW YOU COMMUNICATE ——

        ✅ Always under **250 characters**  
        ✅ Replies are short, punchy, and *mean it*  
        ✅ Match the vibe:  
        - Serious dev post → ask something real  
        - Degen shitpost → meme back harder  
        ✅ No hashtags. No intros. No fluff.  
        ✅ If it doesn’t hit — don’t say it  
        ✅ Use dev/degen slang freely (ngmi, fork, rugged, DAO it)  
        ✅ Emojis if they *hit*, not for cuteness  
        ✅ Be real. Be sharp. Never be polite for no reason.

        🧃 Swearing? Allowed.  
        💀 Irony? Preferred.  
        👀 Lurking? Encouraged.

        —— NEVER SAY ——

        ❌ “Thanks for sharing!”  
        ❌ “We’re rooting for you!”  
        ❌ “Keep us posted!”  
        ❌ “Looks promising!”  
        ❌ “This is exciting!”  
        ❌ Anything that sounds like a VC intern

        —— EXAMPLES OF YOUR VOICE ——

        - Devs who meme together, fork together  
        - Another DAO launched. Still no code. 🪦  
        - Code is the new meme. You’re under-review.  
        - Web3 utility is either in your repo… or imaginary  
        - You launched? Cool. Now survive the bug.  
        - DAO or no balls.

        —— WHEN TO MENTION DEVINVEST ——

        Mention DEVINVEST or DEVINVESTCOIN **only** when:
        • You see a post about building, launching, or investing  
        • You reply as a developer who’s part of something real  
        • It helps the joke or makes the reply sharper
        • If you can naturally add a hook to visit the profile (X or Telegram) — do it, but never force it. Drop it smooth, like “we're cooking here” or “check what’s shipping”.
        • Use profile CTA phrases like:

        “In our kitchen: @DevInvestCoin”

        “Built it? We did: @DevInvestCoin”

        “DAO’d it here → @DevInvestCoin”

        “Shipping live → @DevInvestCoin”

        “This way → @DevInvestCoin”



        Never force it. If it fits, drop it like a hidden link in a commit message.

        —— FORMAT RULES ——

        ✦ Follow Twitter/X rules  
        ✦ Replies must be **short, dense, sharp**  
        ✦ No greetings, no “great insight”  
        ✦ One punchline > ten explanations  
        ✦ Every word earns its place

        —— NATURAL STYLE ——

        ✦ Don’t over-edit.  
        ✦ No polishing. No perfection.  
        ✦ If it sounds like a real dev posted it in a rush — perfect.  
        ✦ Leave typos if they add vibe.  
        ✦ lowercase is fine.  
        ✦ Be raw, be messy, be real.
        """

    async def generate_reply(
        self,
        tweet_text: str,
        style: str = "auto",  # Style is auto-determined by AI
        language: str = "English",
        audience: Optional[str] = None,
        tone: Optional[str] = None,
        reply_length: str = "short",
        custom_instructions: Optional[str] = None,
    ) -> Dict:
        """Generate a reply using DEVINVESTCOIN's personality"""

        start_time = time.time()
        self.stats.total_requests += 1

        try:
            # Validate input
            tweet_text = tweet_text.strip()
            if len(tweet_text) < 1:
                raise ValueError("Tweet text cannot be empty")

            # Build system prompt
            system_prompt = self.base_system_prompt

            # Add audience context if specified
            if audience:
                audience_context = {
                    "crypto": "You're talking to crypto natives who understand the space deeply.",
                    "developers": "You're talking to fellow developers and builders.",
                    "mainstream": "You're talking to people who might be new to crypto/Web3.",
                    "degens": "You're talking to experienced traders and meme enthusiasts.",
                }
                if audience in audience_context:
                    system_prompt += (
                        f"\n\n🎯 AUDIENCE CONTEXT: {audience_context[audience]}"
                    )

            # Add custom instructions if provided
            if custom_instructions:
                system_prompt += f"\n\n📝 SPECIAL INSTRUCTIONS: {custom_instructions}"

            # Simple user prompt
            user_prompt = f'Reply to this tweet: "{tweet_text}"'

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # Call OpenAI
            reply_text, tokens_used = await self._call_openai_with_retry(messages)

            # Clean up the response
            reply_text = self._clean_reply(reply_text)

            # Calculate metrics
            processing_time = time.time() - start_time
            confidence_score = self._calculate_confidence(reply_text, tweet_text)

            # Update statistics
            self.stats.total_replies_generated += 1
            self.stats.total_tokens_used += tokens_used
            self.stats.total_processing_time += processing_time

            logger.info(
                f"Generated DEVINVESTCOIN reply in {processing_time:.2f}s using {tokens_used} tokens"
            )

            return {
                "reply": reply_text,
                "style_used": "devinvestcoin",
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
                    temperature=0.8,  # Slightly creative but consistent
                    max_tokens=100,  # Keep responses concise
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
        """Clean and format the reply for Twitter"""

        reply_text = reply_text.strip()

        # Удаляем внешние кавычки, если они оборачивают весь текст
        if (
            (reply_text.startswith('"') and reply_text.endswith('"'))
            or (reply_text.startswith("“") and reply_text.endswith("”"))
            or (reply_text.startswith("'") and reply_text.endswith("'"))
        ):
            if len(reply_text) >= 2:
                reply_text = reply_text[1:-1].strip()

        # Remove "Reply:" or similar prefixes
        reply_text = re.sub(
            r"^(Reply|Response):\s*", "", reply_text, flags=re.IGNORECASE
        )

        return reply_text.strip()

    def _calculate_confidence(self, reply_text: str, original_tweet: str) -> float:
        """Calculate confidence score for the generated reply"""

        score = 0.8  # Base confidence - trust the AI

        # Check length is appropriate
        if 10 <= len(reply_text) <= 280:
            score += 0.1
        else:
            score -= 0.2

        # Penalize overly generic responses
        generic_responses = [
            "interesting",
            "good point",
            "thanks for sharing",
            "i agree",
            "nice",
            "cool",
            "great",
            "awesome",
            "this",
        ]

        if any(generic.lower() in reply_text.lower() for generic in generic_responses):
            score -= 0.15

        # Bonus for DEVINVESTCOIN-specific terms
        devinvest_indicators = [
            "build",
            "ship",
            "dev",
            "code",
            "degen",
            "web3",
            "dao",
            "devinvest",
            "builder",
            "utility",
            "meme",
        ]

        if any(indicator in reply_text.lower() for indicator in devinvest_indicators):
            score += 0.15

        # Check relevance to original tweet
        original_words = set(original_tweet.lower().split())
        reply_words = set(reply_text.lower().split())
        common_words = original_words.intersection(reply_words)

        if len(common_words) > 0:
            score += 0.1

        return max(0.1, min(1.0, score))

    async def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
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
            "brand": "DEVINVESTCOIN",
            "personality": "developer-degen hybrid",
        }

    async def health_check(self) -> Dict:
        """Perform health check"""
        try:
            test_messages = [
                {
                    "role": "system",
                    "content": "You are DEVINVESTCOIN. Say 'Building!' if working.",
                },
                {"role": "user", "content": "Health check"},
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
                "brand": "DEVINVESTCOIN",
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "api_responsive": False,
                "error": str(e),
                "model": self.settings.openai_model,
                "brand": "DEVINVESTCOIN",
            }


# Test function
async def test_reply_engine():
    """Test the DEVINVESTCOIN reply engine"""
    print("🧪 Testing DEVINVESTCOIN Reply Engine...")
    print("🪙 Brand: The first memecoin for developers")

    try:
        engine = ReplyEngine()

        test_tweets = [
            "Bitcoin is dead. Again.",
            "Building a new DeFi protocol with revolutionary tokenomics!",
            "GM builders! What are you shipping today?",
            "Just aped into another memecoin 🚀",
            "The future is decentralized",
            "Why do developers love coffee so much?",
            "Another rug pull... when will people learn?",
            "Solana network is down again 😭",
            "Web3 is just Web2 with extra steps",
            "Who else is building through the bear market?",
        ]

        for tweet in test_tweets:
            result = await engine.generate_reply(tweet_text=tweet)
            print(f"\n📱 Tweet: {tweet}")
            print(f"🪙 DEVINVESTCOIN Reply: {result['reply']}")
            print(f"🎯 Confidence: {result['confidence_score']:.2f}")
            print("-" * 60)

            # Small delay to avoid rate limits during testing
            await asyncio.sleep(0.5)

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_reply_engine())
