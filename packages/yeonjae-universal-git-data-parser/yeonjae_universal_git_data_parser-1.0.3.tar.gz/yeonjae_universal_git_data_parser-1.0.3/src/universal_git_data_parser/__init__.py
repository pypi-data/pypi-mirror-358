"""
Universal Git Data Parser

GitHub, GitLab 등의 웹훅 데이터를 파싱하고 검증하는 범용 모듈입니다.
"""

__version__ = "1.0.0"

# Core service
from .service import GitDataParserService

# Exception handling
from .exceptions import (
    GitDataParserError,
    InvalidPayloadError,
    GitHubAPIError,
    DiffParsingError,
    CommitNotFoundError,
    UnsupportedPlatformError,
    TimestampParsingError,
    FileTooLargeError,
    NetworkTimeoutError,
    RateLimitExceededError
)

# Main models
from .models import (
    Author,
    CommitInfo,
    GitCommit,
    ValidatedEvent,
    FileChange,
    DiffData,
    GitHubPushPayload,
    DiffStats,
    ParsedWebhookData
)

__all__ = [
    '__version__',
    'GitDataParserService',
    'Author',
    'CommitInfo', 
    'GitCommit',
    'ValidatedEvent',
    'FileChange',
    'DiffData',
    'GitHubPushPayload',
    'DiffStats',
    'ParsedWebhookData',
    'GitDataParserError',
    'InvalidPayloadError',
    'GitHubAPIError',
    'DiffParsingError',
    'CommitNotFoundError',
    'UnsupportedPlatformError',
    'TimestampParsingError',
    'FileTooLargeError',
    'NetworkTimeoutError',
    'RateLimitExceededError'
]
