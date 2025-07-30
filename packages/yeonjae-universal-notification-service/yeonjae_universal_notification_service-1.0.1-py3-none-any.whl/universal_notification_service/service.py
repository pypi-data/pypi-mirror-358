"""
NotificationService 서비스

Slack으로 일일 요약 보고서를 전송하는 범용 알림 모듈입니다.
"""

import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

from .models import (
    NotificationInput, NotificationResult, NotificationChannel,
    NotificationConfig, RecipientInfo, SendStatus, DeliveryAttempt
)
from .exceptions import (
    NotificationServiceException, UnsupportedChannelException,
    SendFailedException, ChannelNotConfiguredException
)

logger = logging.getLogger(__name__)


class NotificationService:
    """알림 서비스"""
    
    def __init__(self):
        self.slack_token = os.getenv("SLACK_BOT_TOKEN")
        self.webhook_url = os.getenv("WEBHOOK_URL")
        logger.info("NotificationService initialized")
    
    async def send_notification(self, input_data: NotificationInput) -> NotificationResult:
        """주요 알림 전송 메서드"""
        try:
            start_time = datetime.now()
            
            # 메시지 포맷팅
            formatted_message = self._format_message(
                input_data.summary_report,
                input_data.formatting_options
            )
            
            # 채널별 전송
            response_data = await self._send_to_channel(
                formatted_message,
                input_data.notification_config,
                input_data.recipient_info
            )
            
            # 성공 결과
            attempt = DeliveryAttempt(
                attempt_number=1,
                timestamp=start_time,
                status=SendStatus.SUCCESS,
                response_data=response_data,
                duration=(datetime.now() - start_time).total_seconds()
            )
            
            return NotificationResult(
                send_status=SendStatus.SUCCESS,
                delivery_attempts=[attempt],
                message_id=response_data.get("message_id"),
                sent_at=start_time
            )
            
        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            
            attempt = DeliveryAttempt(
                attempt_number=1,
                timestamp=datetime.now(),
                status=SendStatus.FAILED,
                error_message=str(e)
            )
            
            return NotificationResult(
                send_status=SendStatus.FAILED,
                delivery_attempts=[attempt],
                error_details={"error": str(e)}
            )
    
    async def send_daily_summary(self, summary_report: str, developer: str, 
                                developer_email: str, slack_channel: str = "#dev-reports") -> NotificationResult:
        """일일 요약 보고서 전송"""
        notification_config = NotificationConfig(
            channel=NotificationChannel.SLACK,
            channel_id=slack_channel,
            mention=True
        )
        
        recipient_info = RecipientInfo(
            developer=developer,
            developer_email=developer_email
        )
        
        input_data = NotificationInput(
            summary_report=summary_report,
            notification_config=notification_config,
            recipient_info=recipient_info
        )
        
        return await self.send_notification(input_data)
    
    async def _send_to_channel(self, message: str, config: NotificationConfig,
                              recipient: RecipientInfo) -> Dict[str, Any]:
        """채널별 전송 처리"""
        if config.channel == NotificationChannel.SLACK:
            return await self._send_slack_message(message, config, recipient)
        elif config.channel == NotificationChannel.EMAIL:
            return await self._send_email_message(message, config, recipient)
        elif config.channel == NotificationChannel.WEBHOOK:
            return await self._send_webhook_message(message, config, recipient)
        else:
            raise UnsupportedChannelException(config.channel.value)
    
    async def _send_slack_message(self, message: str, config: NotificationConfig,
                                 recipient: RecipientInfo) -> Dict[str, Any]:
        """Slack 메시지 전송"""
        if not self.slack_token:
            raise ChannelNotConfiguredException("slack")
        
        try:
            # Mock Slack API 호출
            await asyncio.sleep(0.3)
            
            # 멘션 추가
            if config.mention and recipient.slack_id:
                message = f"<@{recipient.slack_id}>\n\n{message}"
            
            return {
                "ok": True,
                "channel": config.channel_id,
                "message_id": f"slack_msg_{int(time.time())}",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise SendFailedException("slack", e)
    
    async def _send_email_message(self, message: str, config: NotificationConfig,
                                 recipient: RecipientInfo) -> Dict[str, Any]:
        """이메일 메시지 전송"""
        try:
            # Mock 이메일 전송
            await asyncio.sleep(0.5)
            
            return {
                "message_id": f"email_msg_{int(time.time())}",
                "to": recipient.developer_email,
                "subject": f"일일 개발 요약 - {recipient.developer}",
                "sent_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise SendFailedException("email", e)
    
    async def _send_webhook_message(self, message: str, config: NotificationConfig,
                                   recipient: RecipientInfo) -> Dict[str, Any]:
        """웹훅 메시지 전송"""
        if not self.webhook_url:
            raise ChannelNotConfiguredException("webhook")
        
        try:
            # Mock 웹훅 호출
            await asyncio.sleep(0.2)
            
            return {
                "webhook_response": "success",
                "message_id": f"webhook_msg_{int(time.time())}",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise SendFailedException("webhook", e)
    
    def _format_message(self, message: str, formatting_options) -> str:
        """메시지 포맷팅"""
        if not formatting_options:
            return message
        
        formatted = message
        
        # 이모지 제거
        if not formatting_options.include_emoji:
            import re
            formatted = re.sub(r'[🔍📊🚀📈⏰✅⚠️💡📋💭🎯]', '', formatted)
        
        # 길이 제한
        if formatting_options.max_length and len(formatted) > formatting_options.max_length:
            formatted = formatted[:formatting_options.max_length] + "..."
        
        return formatted
    
    def get_supported_channels(self) -> List[NotificationChannel]:
        """지원되는 채널 목록"""
        channels = [NotificationChannel.EMAIL]  # 기본 지원
        
        if self.slack_token:
            channels.append(NotificationChannel.SLACK)
        
        if self.webhook_url:
            channels.append(NotificationChannel.WEBHOOK)
        
        return channels
    
    def is_channel_configured(self, channel: NotificationChannel) -> bool:
        """채널 설정 여부 확인"""
        if channel == NotificationChannel.SLACK:
            return bool(self.slack_token)
        elif channel == NotificationChannel.WEBHOOK:
            return bool(self.webhook_url)
        elif channel == NotificationChannel.EMAIL:
            return True  # 기본 지원
        else:
            return False 