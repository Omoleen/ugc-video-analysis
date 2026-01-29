# UGC Video Analysis

Slack-integrated UGC video review system using Google Gemini AI.

## Overview

This system allows creators to post videos to a Slack channel for automated AI analysis. Videos are scored based on hook effectiveness, narrative structure, technical quality, and call-to-action. High-scoring videos (80+) are eligible for promotion with AI-generated engagement comments.

## Flow

```
Creator posts video → Gemini analyzes → Bot replies with review
                                              ↓
                                    If score >= 80:
                                              ↓
                              Bot prompts for IG/TikTok links
                                              ↓
                              Creator replies with links
                                              ↓
                              Bot generates engagement comments
                                              ↓
                              Posts to #approved-content channel
```

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (optional, for containerized deployment)
- Slack workspace with admin access
- Google Gemini API key

### 1. Clone and Install

```bash
git clone <repository-url>
cd ugc-video-analysis
make install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Create Slack App

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click "Create New App" → "From an app manifest"
3. Select your workspace
4. Paste the following manifest:

```yaml
display_information:
  name: UGC Video Analyzer
  description: Analyzes UGC videos and generates engagement comments
  background_color: "#4A154B"
features:
  bot_user:
    display_name: UGC Analyzer
    always_online: true
oauth_config:
  scopes:
    bot:
      - channels:history
      - channels:read
      - chat:write
      - files:read
settings:
  event_subscriptions:
    bot_events:
      - message.channels
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false
```

5. Install the app to your workspace
6. Copy the Bot Token (`xoxb-...`) and Signing Secret to your `.env`

### 4. Configure Channels

1. Create two channels:
   - `#video-review` - Where creators post videos
   - `#approved-content` - Where approved content gets posted
2. Right-click each channel → "View channel details" → Copy the Channel ID
3. Add the IDs to your `.env`:
   ```
   VIDEO_REVIEW_CHANNEL=C0XXXXXX
   APPROVED_CONTENT_CHANNEL=C0YYYYYY
   ```
4. Invite the bot to both channels: `/invite @UGC Analyzer`

### 5. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key
3. Add to your `.env`: `GEMINI_API_KEY=your-key`

### 6. Run the Application

**With Docker (recommended):**

```bash
make up          # Start app + ngrok
make logs        # View logs
make ngrok-url   # Get public URL for Slack
```

**Without Docker:**

```bash
make dev         # Run with hot reload

# In another terminal:
ngrok http 3000
```

### 7. Configure Slack Event URL

1. Get your public URL from ngrok
2. Go to your Slack app settings → Event Subscriptions
3. Enable Events
4. Set Request URL to: `https://your-ngrok-url/slack/events`
5. Wait for verification, then save

## Usage

1. Post a video to `#video-review`
2. Wait for the AI analysis (can take 30-60 seconds)
3. If your score is 80+, you'll be prompted to share your IG/TikTok links
4. Reply in the thread with your post URLs
5. Engagement comments will be generated and posted to `#approved-content`

## Evaluation Criteria

Videos are scored on a 100-point scale:

| Category | Weight | Description |
|----------|--------|-------------|
| Hook | 40% | First 3 seconds impact, pattern interruption, curiosity gap |
| Narrative | 30% | Story flow, emotional engagement, authenticity |
| Technical | 15% | Video/audio quality, lighting, editing |
| CTA | 15% | Call-to-action clarity, urgency, brand alignment |

## Commands

```bash
make help        # Show all available commands
make install     # Install dependencies
make dev         # Run locally with hot reload
make up          # Start Docker services
make down        # Stop Docker services
make logs        # View container logs
make ngrok-url   # Get ngrok public URL
```

## Project Structure

```
ugc-video-analysis/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment configuration
│   ├── slack_app.py         # Slack Bolt setup
│   ├── services/
│   │   ├── gemini_service.py    # Video analysis
│   │   ├── slack_service.py     # File downloads
│   │   └── score_parser.py      # Score extraction
│   ├── handlers/
│   │   ├── video_handler.py     # Video upload handling
│   │   └── thread_handler.py    # Link collection
│   └── prompts/
│       ├── video_review.py      # Analysis prompt
│       └── comment_generation.py # Comment prompt
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── pyproject.toml
```

## Troubleshooting

**Bot doesn't respond to videos:**
- Ensure bot is invited to the channel
- Check that the channel ID in `.env` matches
- View logs with `make logs`

**Video analysis fails:**
- Check Gemini API key is valid
- Ensure video file is under 2GB
- Check supported formats (mp4, mov, avi, etc.)

**ngrok URL changes:**
- Free ngrok URLs change on restart
- Update Slack Event URL each time
- Consider ngrok paid plan for static URLs
