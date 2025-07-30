"""
Universal Webhook Receiver 기본 테스트

모듈의 기본 임포트와 구조를 테스트합니다.
"""

import pytest
from datetime import datetime


def test_models_import():
    """모델 임포트 테스트"""
    from universal_webhook_receiver.models import (
        WebhookSource, WebhookStatus, WebhookPayload,
        WebhookRequest, WebhookResponse, ProcessingResult
    )
    
    # 열거형 값 확인
    assert WebhookSource.GITHUB == "github"
    assert WebhookSource.GITLAB == "gitlab"
    assert WebhookSource.BITBUCKET == "bitbucket"
    assert WebhookStatus.RECEIVED == "received"
    assert WebhookStatus.PROCESSED == "processed"


def test_exceptions_import():
    """예외 클래스 임포트 테스트"""
    from universal_webhook_receiver.exceptions import (
        WebhookReceiverException,
        InvalidWebhookException,
        ProcessingException
    )
    
    # 예외 클래스 확인
    assert issubclass(InvalidWebhookException, WebhookReceiverException)
    assert issubclass(ProcessingException, WebhookReceiverException)


def test_webhook_payload_creation():
    """WebhookPayload 생성 테스트"""
    from universal_webhook_receiver.models import WebhookPayload, WebhookSource
    
    payload = WebhookPayload(
        source=WebhookSource.GITHUB,
        event_type="push",
        repository="test-repo",
        data={"commits": [{"id": "abc123"}]}
    )
    
    assert payload.source == WebhookSource.GITHUB
    assert payload.event_type == "push"
    assert payload.repository == "test-repo"
    assert payload.data["commits"][0]["id"] == "abc123"


def test_webhook_request_creation():
    """WebhookRequest 생성 테스트"""
    from universal_webhook_receiver.models import WebhookRequest, WebhookSource
    
    request = WebhookRequest(
        source=WebhookSource.GITHUB,
        headers={"X-GitHub-Event": "push"},
        body='{"ref": "refs/heads/main"}',
        signature="sha256=abc123"
    )
    
    assert request.source == WebhookSource.GITHUB
    assert request.headers["X-GitHub-Event"] == "push"
    assert request.body == '{"ref": "refs/heads/main"}'
    assert request.signature == "sha256=abc123"


def test_processing_result_creation():
    """ProcessingResult 생성 테스트"""
    from universal_webhook_receiver.models import ProcessingResult, WebhookStatus
    
    result = ProcessingResult(
        webhook_id="webhook_123",
        status=WebhookStatus.PROCESSED,
        success=True,
        message="Successfully processed",
        processed_at=datetime.now()
    )
    
    assert result.webhook_id == "webhook_123"
    assert result.status == WebhookStatus.PROCESSED
    assert result.success is True
    assert result.message == "Successfully processed"


def test_exception_creation():
    """예외 생성 테스트"""
    from universal_webhook_receiver.exceptions import InvalidWebhookException
    
    exception = InvalidWebhookException("github", "Invalid signature")
    
    assert "github" in str(exception)
    assert "Invalid signature" in str(exception)
    assert exception.details["source"] == "github"
    assert exception.details["reason"] == "Invalid signature" 