"""
Universal Webhook Receiver Exceptions

웹훅 수신 및 처리와 관련된 예외 클래스들을 정의합니다.
"""


class WebhookReceiverException(Exception):
    """웹훅 수신기 기본 예외"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class InvalidWebhookException(WebhookReceiverException):
    """잘못된 웹훅 예외"""
    def __init__(self, source: str, reason: str):
        message = f"{source}: {reason}"
        details = {
            "source": source,
            "reason": reason
        }
        super().__init__(message, details)


class ProcessingException(WebhookReceiverException):
    """처리 예외"""
    def __init__(self, webhook_id: str, error_message: str):
        message = f"Processing failed for webhook {webhook_id}: {error_message}"
        details = {
            "webhook_id": webhook_id,
            "error_message": error_message
        }
        super().__init__(message, details)


class WebhookProcessingException(WebhookReceiverException):
    """웹훅 처리 예외"""
    def __init__(self, webhook_id: str, error: Exception):
        message = f"Webhook processing failed: {webhook_id}"
        details = {
            "webhook_id": webhook_id,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        super().__init__(message, details)


class WebhookValidationException(WebhookReceiverException):
    """웹훅 검증 예외"""
    def __init__(self, field: str, reason: str):
        message = f"Webhook validation failed for field '{field}': {reason}"
        details = {
            "field": field,
            "reason": reason
        }
        super().__init__(message, details)


class WebhookTimeoutException(WebhookReceiverException):
    """웹훅 처리 타임아웃 예외"""
    def __init__(self, webhook_id: str, timeout_seconds: int):
        message = f"Webhook processing timeout: {webhook_id} (after {timeout_seconds}s)"
        details = {
            "webhook_id": webhook_id,
            "timeout_seconds": timeout_seconds
        }
        super().__init__(message, details)


class WebhookRateLimitException(WebhookReceiverException):
    """웹훅 속도 제한 예외"""
    def __init__(self, source: str, current_rate: int, limit: int):
        message = f"Webhook rate limit exceeded for {source}: {current_rate}/{limit}"
        details = {
            "source": source,
            "current_rate": current_rate,
            "limit": limit
        }
        super().__init__(message, details) 