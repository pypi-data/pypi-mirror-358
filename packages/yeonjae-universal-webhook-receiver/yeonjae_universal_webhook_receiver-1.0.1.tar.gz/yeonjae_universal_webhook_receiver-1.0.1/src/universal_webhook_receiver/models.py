"""
Universal Webhook Receiver Models

웹훅 수신 및 처리를 위한 데이터 모델들을 정의합니다.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class WebhookSource(str, Enum):
    """웹훅 소스"""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    CUSTOM = "custom"


class WebhookStatus(str, Enum):
    """웹훅 처리 상태"""
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    COMPLETED = "completed"
    FAILED = "failed"
    IGNORED = "ignored"


class WebhookPayload(BaseModel):
    """웹훅 페이로드"""
    source: WebhookSource = Field(..., description="웹훅 소스")
    event_type: str = Field(..., description="이벤트 타입")
    repository: str = Field(..., description="저장소 이름")
    data: Dict[str, Any] = Field(..., description="이벤트 데이터")
    timestamp: datetime = Field(default_factory=datetime.now, description="수신 시간")
    
    
class WebhookRequest(BaseModel):
    """웹훅 요청"""
    source: WebhookSource = Field(..., description="웹훅 소스")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP 헤더")
    body: str = Field(..., description="요청 본문 (JSON 문자열)")
    signature: str = Field(..., description="웹훅 서명")
    remote_addr: Optional[str] = Field(None, description="원격 주소")
    

class ProcessingResult(BaseModel):
    """처리 결과"""
    webhook_id: str = Field(..., description="웹훅 ID")
    status: WebhookStatus = Field(..., description="처리 상태")
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="처리 메시지")
    processed_at: datetime = Field(default_factory=datetime.now, description="처리 시간")
    result_data: Optional[Dict[str, Any]] = Field(None, description="처리 결과 데이터")
    error_message: Optional[str] = Field(None, description="에러 메시지")
    processing_time_ms: Optional[float] = Field(None, description="처리 시간(밀리초)")


class WebhookResponse(BaseModel):
    """웹훅 응답"""
    webhook_id: str = Field(..., description="웹훅 ID")
    status: WebhookStatus = Field(..., description="처리 상태")
    message: str = Field(..., description="응답 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")


class WebhookEvent(BaseModel):
    """웹훅 이벤트"""
    event_id: str = Field(..., description="이벤트 ID")
    event_type: str = Field(..., description="이벤트 타입")
    repository: Optional[str] = Field(None, description="저장소")
    branch: Optional[str] = Field(None, description="브랜치")
    commit_hash: Optional[str] = Field(None, description="커밋 해시")
    author: Optional[str] = Field(None, description="작성자")
    timestamp: datetime = Field(..., description="이벤트 시간")


class WebhookConfig(BaseModel):
    """웹훅 설정"""
    enabled: bool = Field(default=True, description="활성화 여부")
    secret_token: Optional[str] = Field(None, description="시크릿 토큰")
    allowed_sources: List[WebhookSource] = Field(default_factory=list, description="허용된 소스")
    rate_limit: int = Field(default=100, description="속도 제한")
    timeout_seconds: int = Field(default=30, description="타임아웃(초)") 