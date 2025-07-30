# Universal Notification Service

Universal notification service supporting Slack, Email, Discord, and webhooks for automated reporting.

## Features

- **Multi-Channel Support**: Slack, Email, Discord, Webhooks, SMS
- **Async Operations**: Full async/await support for all notification operations  
- **Rich Formatting**: Support for emoji, markdown, and channel-specific formatting
- **Batch Processing**: Send notifications to multiple recipients efficiently
- **Retry Logic**: Intelligent retry mechanisms with exponential backoff
- **Template System**: Customizable message templates with variable substitution
- **Rate Limiting**: Built-in rate limiting for API compliance
- **Type Safety**: Complete type annotations with mypy support

## Installation

```bash
# Basic installation
pip install yeonjae-universal-notification-service

# With Slack support
pip install yeonjae-universal-notification-service[slack]

# With Email support  
pip install yeonjae-universal-notification-service[email]

# With Discord support
pip install yeonjae-universal-notification-service[discord]

# With all providers
pip install yeonjae-universal-notification-service[all]
```

## Quick Start

```python
import asyncio
from yeonjae_universal_notification_service import (
    NotificationService, NotificationInput, NotificationChannel,
    NotificationConfig, RecipientInfo
)

async def main():
    # Initialize service
    service = NotificationService()
    
    # Configure notification
    config = NotificationConfig(
        channel=NotificationChannel.SLACK,
        channel_id="#dev-reports"
    )
    
    recipient = RecipientInfo(
        developer="John Doe",
        developer_email="john@example.com",
        slack_id="U1234567890"
    )
    
    # Create notification
    notification = NotificationInput(
        summary_report="🎉 Daily development summary ready!",
        notification_config=config,
        recipient_info=recipient
    )
    
    # Send notification
    result = await service.send_notification(notification)
    print(f"Status: {result.send_status}")
    print(f"Message ID: {result.message_id}")

asyncio.run(main())
```

## Configuration

Set your API keys as environment variables:

```bash
export SLACK_BOT_TOKEN="xoxb-your-slack-bot-token"
export DISCORD_BOT_TOKEN="your-discord-bot-token"
export SMTP_PASSWORD="your-email-password"
```

## Supported Channels

- **Slack**: Rich formatting, mentions, threads, file uploads
- **Email**: HTML/Plain text, attachments, templates
- **Discord**: Embeds, mentions, webhooks
- **Webhooks**: Custom HTTP endpoints with retry logic
- **SMS**: Text messages via various providers

## License

MIT License
