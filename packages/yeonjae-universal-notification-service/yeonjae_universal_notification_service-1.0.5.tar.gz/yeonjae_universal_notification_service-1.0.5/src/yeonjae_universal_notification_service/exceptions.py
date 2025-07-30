"""
NotificationService 모듈의 예외 클래스

알림 서비스와 관련된 모든 예외를 정의합니다.
"""


class NotificationServiceException(Exception):
    """NotificationService 기본 예외"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class UnsupportedChannelException(NotificationServiceException):
    """지원하지 않는 알림 채널인 경우"""
    def __init__(self, channel: str):
        message = f"Unsupported notification channel: {channel}"
        super().__init__(message, {
            "channel": channel,
            "supported_channels": ["slack", "email", "discord", "webhook", "sms"]
        })


class SendFailedException(NotificationServiceException):
    """알림 전송이 실패한 경우"""
    def __init__(self, channel: str, error: Exception, attempt_number: int = 1):
        message = f"Notification send failed for {channel} (attempt {attempt_number})"
        super().__init__(message, {
            "channel": channel,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "attempt_number": attempt_number
        })


class InvalidRecipientException(NotificationServiceException):
    """잘못된 수신자 정보인 경우"""
    def __init__(self, field: str, value: str, reason: str):
        message = f"Invalid recipient {field}: {reason}"
        super().__init__(message, {
            "field": field,
            "value": value,
            "reason": reason
        })


class TemplateRenderException(NotificationServiceException):
    """템플릿 렌더링 중 오류가 발생한 경우"""
    def __init__(self, template_name: str, error: Exception):
        message = f"Template rendering failed for {template_name}"
        super().__init__(message, {
            "template_name": template_name,
            "error_type": type(error).__name__,
            "error_message": str(error)
        })


class ChannelNotConfiguredException(NotificationServiceException):
    """알림 채널이 설정되지 않은 경우"""
    def __init__(self, channel: str):
        message = f"Channel not configured: {channel}"
        super().__init__(message, {
            "channel": channel
        })


class MessageTooLongException(NotificationServiceException):
    """메시지가 너무 긴 경우"""
    def __init__(self, current_length: int, max_length: int, channel: str):
        message = f"Message too long for {channel}: {current_length} > {max_length}"
        super().__init__(message, {
            "current_length": current_length,
            "max_length": max_length,
            "channel": channel,
            "excess": current_length - max_length
        })


class RateLimitException(NotificationServiceException):
    """알림 전송 제한에 걸린 경우"""
    def __init__(self, channel: str, retry_after: int = None):
        message = f"Rate limit exceeded for {channel}"
        super().__init__(message, {
            "channel": channel,
            "retry_after": retry_after
        })


class InvalidFormatException(NotificationServiceException):
    """잘못된 메시지 포맷인 경우"""
    def __init__(self, format_type: str, reason: str):
        message = f"Invalid message format '{format_type}': {reason}"
        super().__init__(message, {
            "format_type": format_type,
            "reason": reason
        })


class WebhookException(NotificationServiceException):
    """웹훅 전송 중 오류가 발생한 경우"""
    def __init__(self, webhook_url: str, status_code: int, response_text: str = ""):
        message = f"Webhook failed: {webhook_url} returned {status_code}"
        super().__init__(message, {
            "webhook_url": webhook_url,
            "status_code": status_code,
            "response_text": response_text
        }) 