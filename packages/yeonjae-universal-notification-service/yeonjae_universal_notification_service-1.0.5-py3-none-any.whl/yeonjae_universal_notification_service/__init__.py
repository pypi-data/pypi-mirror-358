"""
Universal Notification Service

Slack, 이메일, Discord 등 다양한 채널로 알림을 전송하는 범용 모듈입니다.
일일 요약 보고서 전송, 알림 템플릿 관리, 개인화된 알림을 제공합니다.

이 모듈은 AI-driven Modular Design 원칙에 따라 설계되었으며,
다른 프로젝트에서도 독립적으로 사용할 수 있습니다.
"""

__version__ = "1.0.0"

from .service import NotificationService
from .models import (
    NotificationInput,
    NotificationResult,
    NotificationChannel,
    NotificationConfig,
    RecipientInfo,
    SendStatus,
    FormattingOptions,
    DeliveryAttempt,
    MessageTemplate,
    ChannelConfig,
    NotificationHistory,
    BatchNotificationInput,
    BatchNotificationResult,
    NotificationMetrics
)
from .exceptions import (
    NotificationServiceException,
    UnsupportedChannelException,
    SendFailedException,
    InvalidRecipientException,
    TemplateRenderException,
    ChannelNotConfiguredException,
    MessageTooLongException,
    RateLimitException,
    InvalidFormatException,
    WebhookException
)

__all__ = [
    '__version__',
    'NotificationService',
    'NotificationInput',
    'NotificationResult',
    'NotificationChannel',
    'NotificationConfig',
    'RecipientInfo',
    'SendStatus',
    'FormattingOptions',
    'DeliveryAttempt',
    'MessageTemplate',
    'ChannelConfig',
    'NotificationHistory',
    'BatchNotificationInput',
    'BatchNotificationResult',
    'NotificationMetrics',
    'NotificationServiceException',
    'UnsupportedChannelException',
    'SendFailedException',
    'InvalidRecipientException',
    'TemplateRenderException',
    'ChannelNotConfiguredException',
    'MessageTooLongException',
    'RateLimitException',
    'InvalidFormatException',
    'WebhookException'
]
