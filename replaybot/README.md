# 🧠 XinvestAI Reply Generator + Auto-Responder

AI-powered tool for generating intelligent, contextual replies to tweets with customizable personality styles + automatic Twitter monitoring and response system.

## 🎯 What It Does

### 💬 Reply Generator
Transform any tweet into engaging replies with different personalities:
- **Ironic**: Witty, sarcastic responses with subtle humor
- **Supportive**: Encouraging and positive engagement  
- **Analytical**: Data-driven, factual responses
- **Provocative**: Thought-provoking challenges
- **Humorous**: Funny, meme-aware content
- **Educational**: Teaching and explanatory responses

### 🤖 Auto-Responder
Automated Twitter monitoring and response system:
- **Monitor accounts**: Track tweets from crypto influencers
- **Keyword filtering**: Respond to specific topics/keywords
- **Smart targeting**: AI-powered sentiment analysis
- **Safety features**: Rate limiting, blacklists, dry-run mode
- **Multiple styles**: Automatic style selection based on tweet content

## 🚀 Quick Start

### Option 1: Complete Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/xinvest-reply-generator.git
cd xinvest-reply-generator

# Run complete setup (includes Playwright browsers)
python setup.py setup

# Setup Twitter login for auto-responder
python twitter_login.py manual

# Start reply generator API
python setup.py run

# Or start auto-responder
python responder_manager.py interactive
```ername/xinvest-reply-generator.git
cd xinvest-reply-generator

# Run setup script
python setup.py setup

# Start the server
python setup.py run
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium

# Create configuration
python config.py create-env

# Setup Twitter login
python twitter_login.py setup

# Start reply generator API
uvicorn main:app --reload

# Start auto-responder (in another terminal)
python responder_manager.py start
```

### Option 3: Docker

```bash
# Build and run with Docker
docker-compose up --build

# Or just the API service
docker build -t xinvest-reply-generator .
docker run -p 8000:8000 --env-file .env xinvest-reply-generator
```

## 📝 Configuration

Create a `.env` file with your settings:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Twitter Auto-Responder
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password
TWITTER_EMAIL=your_twitter_email

# Optional API Settings
XINVEST_API_KEY=your_custom_api_key
OPENAI_MODEL=gpt-4o-mini
REQUIRE_AUTH=false
DEBUG=true
PORT=8000
```

## 🔧 API Usage

### Generate Single Reply

```bash
curl -X POST "http://localhost:8000/reply" \
  -H "Content-Type: application/json" \
  -d '{
    "tweet": "Bitcoin is dead. Again.",
    "style": "ironic",
    "language": "English",
    "audience": "crypto",
    "reply_length": "short"
  }'
```

**Response:**
```json
{
  "reply": "Wow, we've buried Bitcoin more times than I've lost my keys. Spoiler: it's still alive 😅",
  "style_used": "ironic",
  "tone_used": "friendly",
  "confidence_score": 0.92,
  "processing_time": 1.34,
  "tokens_used": 45
}
```

## 🤖 Auto-Responder Usage

### Interactive Management

```bash
# Start interactive manager
python responder_manager.py interactive

# Or use CLI commands
python responder_manager.py start --live  # Live mode
python responder_manager.py test --tweet "Bitcoin is up 10%"
python responder_manager.py status
```

### Configuration Options

**Safe Testing (Dry Run)**:
```bash
# Test without actually posting
python responder_manager.py start  # Dry run by default
```

**Live Mode**:
```bash
# Actually post responses (be careful!)
python responder_manager.py start --live
```

### Auto-Responder Features

| Feature | Description |
|---------|-------------|
| **Account Monitoring** | Track specific Twitter accounts (Elon, CZ, Vitalik, etc.) |
| **Keyword Filtering** | Respond to tweets containing crypto keywords |
| **Smart Sentiment** | AI detects tweet mood and picks appropriate style |
| **Rate Limiting** | Configurable limits (per hour, per account, daily) |
| **Safety Features** | Dry run, manual approval, blacklisted words |
| **Response Styles** | 6 different AI personalities for responses |

### Default Monitored Accounts
- @elonmusk
- @cb_doge  
- @cz_binance
- @saylor
- @VitalikButerin
- @justinsuntron
- @coinbase

### Monitored Keywords
- bitcoin, btc, ethereum, eth, crypto, blockchain
- defi, nft, web3, altcoin, hodl, moon, pump
- regulation, sec, fed, adoption

## 🎨 Style Examples

| Style | Input: "Bitcoin crashed 50%" | Generated Reply |
|-------|------------------------------|-----------------|
| **Ironic** | | "Ah yes, Bitcoin's 437th death. Should we send flowers? 💀" |
| **Supportive** | | "Tough times create strong HODLers! This is when real wealth is built 💪" |
| **Analytical** | | "50% corrections are historically normal. 2018 was -84%, 2022 was -77%..." |
| **Humorous** | | "My portfolio and I are no longer on speaking terms 📉😅" |
| **Educational** | | "This is called a bear market correction. Historically, these create the best buying opportunities..." |

## 🛠️ Project Structure

```
xinvest-reply-generator/
├── main.py                     # FastAPI application
├── models.py                   # Pydantic models
├── reply_engine.py             # AI reply generation
├── auto_responder.py           # Twitter auto-responder
├── responder_manager.py        # Management interface
├── twitter_login.py            # Login helper
├── config.py                   # Configuration management
├── setup.py                    # Installation script
├── auto_responder_config.json  # Auto-responder settings
├── requirements.txt            # Dependencies
├── Dockerfile                  # Container setup
├── docker-compose.yml          # Multi-service setup
└── tests/                      # Test suite
```

## 🔐 Twitter Authentication

### Method 1: Manual Login (Recommended)
```bash
# Opens browser for manual login
python twitter_login.py manual
```

### Method 2: Automated Login
```bash
# Uses credentials from .env
python twitter_login.py auto
```

### Verify Login
```bash
# Check if login is valid
python twitter_login.py verify
```

## ⚙️ Auto-Responder Configuration

Edit `auto_responder_config.json`:

```json
{
  "accounts_to_monitor": ["elonmusk", "VitalikButerin"],
  "keywords_to_monitor": ["bitcoin", "ethereum", "crypto"],
  "response_styles": {
    "positive_tweets": "supportive",
    "negative_tweets": "analytical",
    "hype_tweets": "humorous"
  },
  "safety": {
    "dry_run": true,
    "max_daily_responses": 30,
    "require_manual_approval": false
  }
}
```

## 🛡️ Safety Features

### Dry Run Mode
- Test responses without actually posting
- See what would be posted
- Perfect for testing and setup

### Rate Limiting
- Max responses per hour/day
- Delays between responses
- Per-account limits

### Content Filtering
- Blacklisted words protection
- Minimum engagement thresholds
- Tweet age limits

### Manual Approval
- Review each response before posting
- Override AI decisions
- Complete control

## 📊 Monitoring & Analytics

### Real-time Stats
```bash
# View current statistics
python responder_manager.py status
```

### Response Tracking
- All responses saved to database
- Engagement tracking
- Performance metrics
- Style effectiveness analysis

## 🚀 Deployment

### Local Executable
```bash
# Build standalone .exe
python setup.py build
```

### Cloud Deployment
```bash
# Railway
railway login && railway init && railway up

# Heroku  
heroku create xinvest-reply-generator
heroku config:set OPENAI_API_KEY=your_key
git push heroku main

# Docker
docker-compose --profile production up -d
```

## 🧪 Testing

### Test Reply Generation
```bash
# Test specific tweet and style
python responder_manager.py test \
  --tweet "Bitcoin is going to the moon!" \
  --style humorous
```

### Run Test Suite
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Test auto-responder specifically
pytest tests/test_auto_responder.py -v
```

## 💡 Use Cases

### Reply Generator
- **Social Media Management**: Generate engaging replies for brand accounts
- **Content Creation**: Create conversational content for blogs/videos
- **Personal Branding**: Maintain consistent voice across platforms

### Auto-Responder
- **Community Engagement**: Automatically engage with crypto community
- **Thought Leadership**: Share insights on trending topics
- **Brand Presence**: Maintain active social media presence
- **Research**: Analyze conversation patterns and responses

## ⚠️ Important Notes

### Auto-Responder Safety
1. **Always start with dry run mode**
2. **Test thoroughly before going live**
3. **Monitor response quality regularly**
4. **Respect Twitter's terms of service**
5. **Use reasonable rate limits**

### Best Practices
- Start with conservative settings
- Monitor engagement rates
- Adjust styles based on audience response
- Regular review of generated content
- Respect community guidelines

## 🔧 Troubleshooting

### Common Issues

**"Playwright browser not found"**
```bash
# Install Playwright browsers
python -m playwright install chromium
```

**"Twitter login failed"**
```bash
# Try manual login
python twitter_login.py manual

# Or clear session and retry
python twitter_login.py clear
python twitter_login.py setup
```

**"OpenAI API errors"**
```bash
# Check API key
python config.py check

# Monitor rate limits
# Consider using gpt-4o-mini for cost efficiency
```

**Auto-responder not finding tweets**
```bash
# Verify login session
python twitter_login.py verify

# Check configuration
python responder_manager.py status

# Enable debug mode
# Set DEBUG=true in .env
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🚀 Roadmap

### Reply Generator
- [ ] Web UI interface
- [ ] Custom style training
- [ ] Multi-language support
- [ ] Sentiment analysis
- [ ] Browser extension

### Auto-Responder
- [ ] Multi-platform support (LinkedIn, Reddit)
- [ ] Advanced AI conversation flows
- [ ] Analytics dashboard
- [ ] A/B testing for styles
- [ ] Integration with CRM systems
- [ ] Scheduled posting
- [ ] Community management features

---

**Built with ❤️ for the crypto community**

*Generate replies that sound human, not robotic. Automate engagement intelligently.*# ReplayAI
