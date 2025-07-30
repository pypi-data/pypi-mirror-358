"""
NotificationService 모듈의 데이터 모델

상세설계서에 정의된 Input/Output 데이터 구조를 정의합니다.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class NotificationChannel(Enum):
    """알림 채널"""
    SLACK = "slack"
    EMAIL = "email"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    SMS = "sms"


class SendStatus(Enum):
    """전송 상태"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    PENDING = "pending"
    RETRY = "retry"


@dataclass
class NotificationConfig:
    """알림 설정"""
    channel: NotificationChannel
    channel_id: str  # "#dev-reports", "user@example.com" 등
    mention: bool = False
    mention_users: List[str] = field(default_factory=list)
    priority: str = "normal"  # low, normal, high, urgent
    retry_count: int = 3
    retry_delay: int = 5  # 초
    
    def __post_init__(self):
        if not self.channel_id:
            raise ValueError("Channel ID is required")


@dataclass
class RecipientInfo:
    """수신자 정보"""
    developer: str
    developer_email: str
    slack_id: Optional[str] = None
    discord_id: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: str = "Asia/Seoul"
    preferred_language: str = "korean"
    
    def get_mention_string(self, channel: NotificationChannel) -> str:
        """채널별 멘션 문자열 반환"""
        if channel == NotificationChannel.SLACK and self.slack_id:
            return f"<@{self.slack_id}>"
        elif channel == NotificationChannel.DISCORD and self.discord_id:
            return f"<@{self.discord_id}>"
        else:
            return self.developer


@dataclass
class FormattingOptions:
    """포매팅 옵션"""
    include_emoji: bool = True
    format_type: str = "rich"  # plain, rich, markdown
    color_scheme: str = "default"  # default, success, warning, error
    max_length: Optional[int] = None
    truncate_strategy: str = "end"  # start, end, middle
    
    def should_truncate(self, text: str) -> bool:
        """텍스트 자르기 필요 여부"""
        return self.max_length is not None and len(text) > self.max_length


@dataclass
class NotificationInput:
    """알림 입력 데이터 (상세설계서 Input 데이터)"""
    summary_report: str
    notification_config: NotificationConfig
    recipient_info: RecipientInfo
    formatting_options: Optional[FormattingOptions] = None
    
    def __post_init__(self):
        if not self.summary_report or not self.summary_report.strip():
            raise ValueError("Summary report cannot be empty")
        
        if self.formatting_options is None:
            self.formatting_options = FormattingOptions()


@dataclass
class DeliveryAttempt:
    """전송 시도 정보"""
    attempt_number: int
    timestamp: datetime
    status: SendStatus
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    duration: float = 0.0  # 전송 소요 시간 (초)
    
    @property
    def is_successful(self) -> bool:
        """성공적인 전송인지 확인"""
        return self.status == SendStatus.SUCCESS


@dataclass
class NotificationResult:
    """알림 결과 데이터 (상세설계서 Output 데이터)"""
    send_status: SendStatus
    delivery_attempts: List[DeliveryAttempt] = field(default_factory=list)
    message_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    error_details: Optional[Dict[str, Any]] = None
    
    @property
    def total_attempts(self) -> int:
        """총 전송 시도 횟수"""
        return len(self.delivery_attempts)
    
    @property
    def last_attempt(self) -> Optional[DeliveryAttempt]:
        """마지막 전송 시도"""
        return self.delivery_attempts[-1] if self.delivery_attempts else None
    
    @property
    def is_successful(self) -> bool:
        """성공적인 전송인지 확인"""
        return self.send_status == SendStatus.SUCCESS
    
    @property
    def total_duration(self) -> float:
        """총 소요 시간"""
        return sum(attempt.duration for attempt in self.delivery_attempts)


@dataclass
class MessageTemplate:
    """메시지 템플릿"""
    name: str
    content: str
    channel: NotificationChannel
    variables: List[str] = field(default_factory=list)
    supports_formatting: bool = True
    
    def get_required_variables(self) -> List[str]:
        """필수 변수 목록"""
        return self.variables


@dataclass
class ChannelConfig:
    """채널별 설정"""
    channel: NotificationChannel
    api_key: Optional[str] = None
    webhook_url: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    rate_limit: Optional[int] = None  # 분당 요청 수
    
    def is_configured(self) -> bool:
        """설정이 완료되었는지 확인"""
        if self.channel == NotificationChannel.SLACK:
            return bool(self.api_key)
        elif self.channel == NotificationChannel.WEBHOOK:
            return bool(self.webhook_url)
        elif self.channel == NotificationChannel.EMAIL:
            return bool(self.api_key)
        return True


@dataclass
class NotificationHistory:
    """알림 히스토리"""
    notification_id: str
    recipient: str
    channel: NotificationChannel
    sent_at: datetime
    status: SendStatus
    message_preview: str
    retry_count: int = 0
    
    def __post_init__(self):
        if not self.notification_id:
            self.notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


@dataclass
class BatchNotificationInput:
    """배치 알림 입력"""
    notifications: List[NotificationInput]
    batch_id: Optional[str] = None
    send_in_parallel: bool = True
    max_concurrent: int = 5
    
    def __post_init__(self):
        if not self.batch_id:
            self.batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not self.notifications:
            raise ValueError("Notifications list cannot be empty")


@dataclass
class BatchNotificationResult:
    """배치 알림 결과"""
    batch_id: str
    total_notifications: int
    successful_count: int
    failed_count: int
    results: List[NotificationResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """성공률"""
        if self.total_notifications == 0:
            return 0.0
        return self.successful_count / self.total_notifications
    
    @property
    def is_completed(self) -> bool:
        """완료 여부"""
        return self.completed_at is not None
    
    @property
    def duration(self) -> float:
        """총 소요 시간 (초)"""
        if not self.completed_at:
            return 0.0
        return (self.completed_at - self.started_at).total_seconds()


@dataclass
class NotificationMetrics:
    """알림 메트릭"""
    total_sent: int
    success_count: int
    failure_count: int
    avg_delivery_time: float
    channel_stats: Dict[str, int] = field(default_factory=dict)
    error_stats: Dict[str, int] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """성공률"""
        if self.total_sent == 0:
            return 0.0
        return self.success_count / self.total_sent
    
    @property
    def failure_rate(self) -> float:
        """실패율"""
        return 1.0 - self.success_rate 