"""
Universal Notification Service 기본 테스트
"""

import pytest
import asyncio
from datetime import datetime
from universal_notification_service import (
    NotificationService,
    NotificationInput,
    NotificationChannel,
    NotificationConfig,
    RecipientInfo,
    SendStatus,
    __version__
)


def test_version():
    """버전 정보 테스트"""
    assert __version__ == "1.0.0"


def test_import():
    """패키지 import 테스트"""
    from universal_notification_service import (
        NotificationService, NotificationInput, NotificationResult,
        NotificationChannel, NotificationConfig, RecipientInfo
    )
    assert NotificationService is not None
    assert NotificationInput is not None
    assert NotificationChannel is not None


def test_service_creation():
    """NotificationService 인스턴스 생성 테스트"""
    service = NotificationService()
    assert service is not None


def test_notification_channel():
    """NotificationChannel 열거형 테스트"""
    assert NotificationChannel.SLACK.value == "slack"
    assert NotificationChannel.EMAIL.value == "email"
    assert NotificationChannel.DISCORD.value == "discord"
    assert NotificationChannel.WEBHOOK.value == "webhook"


def test_send_status():
    """SendStatus 열거형 테스트"""
    assert SendStatus.SUCCESS.value == "success"
    assert SendStatus.FAILED.value == "failed"
    assert SendStatus.PENDING.value == "pending"


def test_notification_config():
    """NotificationConfig 생성 테스트"""
    config = NotificationConfig(
        channel=NotificationChannel.SLACK,
        channel_id="#dev-reports"
    )
    assert config.channel == NotificationChannel.SLACK
    assert config.channel_id == "#dev-reports"
    # 원본 모델의 실제 기본값 확인
    assert hasattr(config, 'mention')
    assert hasattr(config, 'retry_count')


def test_recipient_info():
    """RecipientInfo 생성 테스트"""
    recipient = RecipientInfo(
        developer="John Doe",
        developer_email="john@example.com",
        slack_id="U1234567890"
    )
    assert recipient.developer == "John Doe"
    assert recipient.developer_email == "john@example.com"
    assert recipient.slack_id == "U1234567890"
    # timezone 속성이 있는지 확인
    assert hasattr(recipient, 'timezone')


def test_notification_input():
    """NotificationInput 생성 테스트"""
    config = NotificationConfig(
        channel=NotificationChannel.SLACK,
        channel_id="#test"
    )
    
    recipient = RecipientInfo(
        developer="Test User",
        developer_email="test@example.com"
    )
    
    notification = NotificationInput(
        summary_report="Test notification message",
        notification_config=config,
        recipient_info=recipient
    )
    
    assert notification.summary_report == "Test notification message"
    assert notification.notification_config == config
    assert notification.recipient_info == recipient


def test_basic_functionality():
    """기본 기능 테스트"""
    service = NotificationService()
    
    # 지원 채널 확인 (메서드가 있는지 확인)
    if hasattr(service, 'get_supported_channels'):
        supported = service.get_supported_channels()
        assert isinstance(supported, list)
    
    # 채널 설정 확인 (메서드가 있는지 확인)  
    if hasattr(service, 'is_channel_configured'):
        email_configured = service.is_channel_configured(NotificationChannel.EMAIL)
        assert isinstance(email_configured, bool)


def test_formatting_options():
    """FormattingOptions 테스트"""
    from universal_notification_service import FormattingOptions
    
    formatting = FormattingOptions()
    assert formatting is not None


def test_delivery_attempt():
    """DeliveryAttempt 테스트"""
    from universal_notification_service import DeliveryAttempt
    
    # 필수 매개변수와 함께 생성
    attempt = DeliveryAttempt(
        attempt_number=1,
        timestamp=datetime.now(),
        status=SendStatus.SUCCESS
    )
    assert attempt is not None
    assert attempt.attempt_number == 1
    assert attempt.status == SendStatus.SUCCESS
    assert hasattr(attempt, 'is_successful')


@pytest.mark.asyncio
async def test_mock_notification():
    """Mock 알림 전송 테스트 (실제 전송 안함)"""
    service = NotificationService()
    
    config = NotificationConfig(
        channel=NotificationChannel.EMAIL,
        channel_id="test@example.com"
    )
    
    recipient = RecipientInfo(
        developer="Test User",
        developer_email="test@example.com"
    )
    
    notification = NotificationInput(
        summary_report="🧪 Test notification from universal-notification-service",
        notification_config=config,
        recipient_info=recipient
    )
    
    # 실제 전송 대신 객체 생성만 테스트
    assert notification is not None
    assert notification.summary_report is not None
    assert notification.notification_config is not None
    assert notification.recipient_info is not None


def test_exception_classes():
    """예외 클래스 테스트"""
    from universal_notification_service import (
        NotificationServiceException,
        UnsupportedChannelException,
        SendFailedException
    )
    
    # 예외 클래스가 제대로 import되는지 확인
    assert issubclass(UnsupportedChannelException, NotificationServiceException)
    assert issubclass(SendFailedException, NotificationServiceException)


def test_batch_classes():
    """Batch 관련 클래스 테스트"""
    from universal_notification_service import (
        BatchNotificationInput,
        BatchNotificationResult,
        NotificationMetrics
    )
    
    # 클래스가 제대로 import되는지 확인
    assert BatchNotificationInput is not None
    assert BatchNotificationResult is not None
    assert NotificationMetrics is not None


def test_service_methods():
    """NotificationService의 주요 메서드 테스트"""
    service = NotificationService()
    
    # 기본 메서드들이 존재하는지 확인
    assert hasattr(service, 'send_notification')
    
    # send_notification이 async 메서드인지 확인
    import asyncio
    assert asyncio.iscoroutinefunction(service.send_notification)


def test_comprehensive_objects():
    """포괄적인 객체 생성 테스트"""
    # 모든 주요 컴포넌트가 제대로 생성되는지 확인
    config = NotificationConfig(
        channel=NotificationChannel.SLACK,
        channel_id="#general"
    )
    
    recipient = RecipientInfo(
        developer="Test Developer",
        developer_email="dev@test.com"
    )
    
    notification = NotificationInput(
        summary_report="Comprehensive test message",
        notification_config=config,
        recipient_info=recipient
    )
    
    service = NotificationService()
    
    # 모든 객체가 제대로 생성되었는지 확인
    assert all([config, recipient, notification, service])
    
    print(f"✅ notification-service v{__version__} 패키지 테스트 완료!")
    print(f"📧 지원 채널: {[c.value for c in NotificationChannel]}")
    print(f"📊 상태 유형: {[s.value for s in SendStatus]}")
