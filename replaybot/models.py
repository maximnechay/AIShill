from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from enum import Enum


class StyleType(str, Enum):
    """Available reply styles"""

    IRONIC = "ironic"
    SUPPORTIVE = "supportive"
    ANALYTICAL = "analytical"
    PROVOCATIVE = "provocative"
    HUMOROUS = "humorous"
    EDUCATIONAL = "educational"
    NEUTRAL = "neutral"


class ToneType(str, Enum):
    """Available tone options"""

    FRIENDLY = "friendly"
    SARCASTIC = "sarcastic"
    AGGRESSIVE = "aggressive"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    WITTY = "witty"


class ReplyLength(str, Enum):
    """Reply length options"""

    SHORT = "short"  # 1-2 sentences, ~280 chars
    MEDIUM = "medium"  # 2-3 sentences, ~400 chars
    LONG = "long"  # 3-5 sentences, ~600 chars


class AudienceType(str, Enum):
    """Target audience types"""

    CRYPTO = "crypto"
    FINANCE = "finance"
    TECH = "tech"
    GENERAL = "general"
    BUSINESS = "business"
    ACADEMIC = "academic"


class TweetReplyRequest(BaseModel):
    """Request model for single tweet reply generation"""

    tweet: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Original tweet text to reply to",
    )
    style: StyleType = Field(
        default=StyleType.NEUTRAL, description="Reply style/personality"
    )
    language: str = Field(default="English", description="Response language")
    audience: Optional[AudienceType] = Field(
        None, description="Target audience for tone adjustment"
    )
    tone: Optional[ToneType] = Field(None, description="Specific tone within the style")
    reply_length: ReplyLength = Field(
        default=ReplyLength.MEDIUM, description="Desired length of reply"
    )
    custom_instructions: Optional[str] = Field(
        None, max_length=500, description="Additional custom instructions"
    )

    class Config:
        schema_extra = {
            "example": {
                "tweet": "Bitcoin is dead. Again.",
                "style": "ironic",
                "language": "English",
                "audience": "crypto",
                "tone": "friendly",
                "reply_length": "short",
                "custom_instructions": "Add a rocket emoji at the end",
            }
        }


class TweetReplyResponse(BaseModel):
    """Response model for single tweet reply"""

    reply: str = Field(..., description="Generated reply text")
    style_used: str = Field(..., description="Style that was applied")
    tone_used: str = Field(..., description="Tone that was applied")
    language_used: str = Field(..., description="Language of the response")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="AI confidence in the response quality"
    )
    processing_time: float = Field(
        ..., description="Time taken to generate response (seconds)"
    )
    tokens_used: int = Field(..., description="Number of AI tokens consumed")

    class Config:
        schema_extra = {
            "example": {
                "reply": "Wow, we've buried Bitcoin more times than I've lost my keys. Spoiler: it's still alive 😅",
                "style_used": "ironic",
                "tone_used": "friendly",
                "language_used": "English",
                "confidence_score": 0.92,
                "processing_time": 1.34,
                "tokens_used": 45,
            }
        }


class BulkTweetData(BaseModel):
    """Individual tweet data for bulk processing"""

    tweet: str = Field(..., min_length=1, max_length=2000)
    style: Optional[StyleType] = Field(
        None, description="Override default style for this tweet"
    )

    class Config:
        schema_extra = {
            "example": {"tweet": "ETH is going to the moon!", "style": "humorous"}
        }


class BulkReplySettings(BaseModel):
    """Global settings for bulk reply generation"""

    language: str = Field(default="English")
    audience: Optional[AudienceType] = Field(None)
    tone: Optional[ToneType] = Field(None)
    reply_length: ReplyLength = Field(default=ReplyLength.MEDIUM)


class BulkReplyRequest(BaseModel):
    """Request model for bulk tweet reply generation"""

    tweets: List[BulkTweetData] = Field(
        ..., min_items=1, max_items=50, description="List of tweets to process"
    )
    default_style: StyleType = Field(
        default=StyleType.NEUTRAL, description="Default style for all tweets"
    )
    settings: Optional[BulkReplySettings] = Field(
        None, description="Global settings for all replies"
    )

    @validator("tweets")
    def validate_tweets_count(cls, v):
        if len(v) > 50:
            raise ValueError("Maximum 50 tweets per bulk request")
        return v

    class Config:
        schema_extra = {
            "example": {
                "tweets": [
                    {"tweet": "Bitcoin is dead. Again.", "style": "ironic"},
                    {"tweet": "ETH to the moon! 🚀"},
                    {"tweet": "DeFi is the future of finance"},
                ],
                "default_style": "analytical",
                "settings": {
                    "language": "English",
                    "audience": "crypto",
                    "reply_length": "short",
                },
            }
        }


class BulkReplyResult(BaseModel):
    """Individual result in bulk processing"""

    index: int = Field(..., description="Original index in the request")
    original_tweet: str = Field(..., description="Original tweet text")
    reply: Optional[str] = Field(None, description="Generated reply (null if failed)")
    style_used: Optional[str] = Field(None, description="Style that was applied")
    success: bool = Field(..., description="Whether generation was successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    tokens_used: int = Field(default=0, description="Tokens used for this reply")


class BulkReplyResponse(BaseModel):
    """Response model for bulk tweet reply generation"""

    results: List[BulkReplyResult] = Field(..., description="Results for each tweet")
    total_processed: int = Field(..., description="Total number of tweets processed")
    successful_count: int = Field(..., description="Number of successful generations")
    failed_count: int = Field(..., description="Number of failed generations")
    total_tokens_used: int = Field(..., description="Total tokens consumed")

    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "index": 0,
                        "original_tweet": "Bitcoin is dead. Again.",
                        "reply": "Ah yes, Bitcoin's 437th death. Should we send flowers? 💀",
                        "style_used": "ironic",
                        "success": True,
                        "tokens_used": 32,
                    }
                ],
                "total_processed": 3,
                "successful_count": 3,
                "failed_count": 0,
                "total_tokens_used": 127,
            }
        }


class StylePreset(BaseModel):
    """Predefined style configuration"""

    name: str = Field(..., description="Style name")
    description: str = Field(..., description="Style description")
    system_prompt: str = Field(..., description="System prompt for this style")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="AI creativity level"
    )
    max_tokens: int = Field(
        default=150, ge=10, le=500, description="Maximum response length"
    )
    examples: List[str] = Field(
        default=[], description="Example responses in this style"
    )


class ServiceStats(BaseModel):
    """Service statistics model"""

    total_requests: int = Field(default=0)
    total_replies_generated: int = Field(default=0)
    total_tokens_used: int = Field(default=0)
    average_processing_time: float = Field(default=0.0)
    style_usage: Dict[str, int] = Field(default={})
    uptime_seconds: float = Field(default=0.0)


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error description")
    error_code: Optional[str] = Field(None, description="Error code for categorization")

    class Config:
        schema_extra = {
            "example": {
                "error": "Invalid API key",
                "detail": "The provided API key is not valid or has expired",
                "error_code": "AUTH_001",
            }
        }
