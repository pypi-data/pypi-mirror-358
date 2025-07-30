"""GitHub webhook data parser for validated events."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, ValidationError

from .models import (
    GitCommit,
    ValidatedEvent,
    CommitInfo,
    Author,
    DiffData,
    GitHubPushPayload,
    DiffStats,
    ParsedWebhookData,
    FileChange,
)
from .exceptions import (
    InvalidPayloadError,
    GitHubAPIError,
    DiffParsingError,
    CommitNotFoundError,
    UnsupportedPlatformError,
    TimestampParsingError,
    FileTooLargeError,
    NetworkTimeoutError,
    RateLimitExceededError,
)

logger = logging.getLogger(__name__)


class GitDataParserService:
    """GitHub webhook 데이터 파싱 및 diff 분석 서비스."""

    def __init__(self, github_token: Optional[str] = None, timeout: int = 30):
        """
        Args:
            github_token: GitHub API 토큰 (diff 가져오기용)
            timeout: API 요청 타임아웃 (초)
        """
        self.github_token = github_token
        self.timeout = timeout

    def parse_github_push(self, headers: Dict[str, str], payload: Dict[str, Any]) -> ValidatedEvent:
        """
        GitHub push webhook 이벤트를 파싱하여 ValidatedEvent 반환
        """
        logger.debug("Parsing GitHub push event")
        
        try:
            # Repository 정보 추출
            repo_info = payload.get("repository", {})
            repository = repo_info.get("full_name")
            if not repository:
                raise InvalidPayloadError("Missing repository full_name")

            # Ref 정보 (브랜치)
            ref = payload.get("ref", "")
            
            # Pusher 정보 추출
            pusher_info = payload.get("pusher", {})
            pusher = pusher_info.get("name", pusher_info.get("login", "unknown"))

            # Commits 파싱 - GitCommit 모델 사용 (ValidatedEvent와 호환)
            commits_data = payload.get("commits", [])
            commits = []
            
            for commit_data in commits_data:
                try:
                    # Author 정보 파싱 (GitCommit은 author를 문자열로 저장)
                    author_data = commit_data.get("author", {})
                    author_name = author_data.get("name", "Unknown")
                    
                    # Timestamp 파싱
                    timestamp_str = commit_data.get("timestamp")
                    if timestamp_str:
                        # ISO 형식의 timestamp 파싱
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except ValueError:
                            timestamp = datetime.utcnow()
                    else:
                        timestamp = datetime.utcnow()
                    
                    # GitCommit 생성 (ValidatedEvent와 호환)
                    git_commit = GitCommit(
                        id=commit_data.get("id", ""),
                        message=commit_data.get("message", ""),
                        url=commit_data.get("url", ""),
                        author=author_name,
                        timestamp=timestamp,
                        added=commit_data.get("added", []),
                        modified=commit_data.get("modified", []),
                        removed=commit_data.get("removed", [])
                    )
                    commits.append(git_commit)
                    
                except Exception as e:
                    logger.warning("Failed to parse commit: %s", str(e))
                    continue

            # ValidatedEvent 생성
            validated_event = ValidatedEvent(
                repository=repository,
                ref=ref,
                pusher=pusher,
                commits=commits
            )
            
            logger.debug("Successfully parsed %d commits for %s", len(commits), repository)
            return validated_event
            
        except Exception as e:
            logger.error("Failed to parse GitHub push event: %s", str(e))
            raise InvalidPayloadError(f"Failed to parse push event: {str(e)}")

    def parse_webhook_data(self, payload: Dict[str, Any], headers: Dict[str, str]) -> ParsedWebhookData:
        """
        GitHub webhook payload를 구조화된 데이터로 변환 (순수 파싱, API 호출 없음)
        """
        logger.debug("parse_webhook_data input: repository=%s, commits=%d", 
                    payload.get("repository", {}).get("full_name", "unknown"),
                    len(payload.get("commits", [])))
        
        try:
            # 1. Repository 정보 추출
            if "repository" not in payload:
                raise InvalidPayloadError("Missing 'repository' field", missing_fields=["repository"])
            
            repository = payload["repository"]["full_name"]
            
            # 2. Branch 정보 추출 (ref)
            ref = payload.get("ref", "refs/heads/main")
            branch = ref.replace("refs/heads/", "")
            
            # 3. Commits 정보 파싱
            raw_commits = payload.get("commits", [])
            commits: List[GitCommit] = []
            
            for commit_data in raw_commits:
                try:
                    timestamp_str = commit_data.get("timestamp")
                    if timestamp_str:
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except ValueError as e:
                            logger.warning("Invalid timestamp format %s: %s", timestamp_str, e)
                            timestamp = datetime.utcnow()
                    else:
                        timestamp = datetime.utcnow()
                    
                    # Author 정보
                    author_data = commit_data.get("author", {})
                    author = Author(
                        name=author_data.get("name", "Unknown"),
                        email=author_data.get("email", "unknown@example.com")
                    )
                    
                    commit = GitCommit(
                        id=commit_data.get("id", ""),
                        message=commit_data.get("message", ""),
                        author=author,
                        timestamp=timestamp,
                        url=commit_data.get("url", ""),
                        added=commit_data.get("added", []),
                        modified=commit_data.get("modified", []),
                        removed=commit_data.get("removed", [])
                    )
                    commits.append(commit)
                    
                except Exception as e:
                    logger.error("Error parsing commit %s: %s", 
                               commit_data.get("id", "unknown"), e)
                    # 개별 커밋 파싱 실패는 전체 처리를 중단하지 않음
                    continue
            
            # 4. Diff 통계 계산 (파일 변경 정보 기반)
            total_added = sum(len(c.added) for c in commits)
            total_modified = sum(len(c.modified) for c in commits)
            total_removed = sum(len(c.removed) for c in commits)
            
            diff_stats = DiffStats(
                files_changed=total_added + total_modified + total_removed,
                lines_added=0,  # webhook에서는 라인 수 정보 없음
                lines_deleted=0,
                total_changes=total_added + total_modified + total_removed
            )
            
            # 5. 결과 생성
            result = ParsedWebhookData(
                repository=repository,
                branch=branch,
                commits=commits,
                diff_stats=diff_stats,
                timestamp=datetime.utcnow()
            )
            
            logger.debug("parse_webhook_data output: repository=%s, commits_parsed=%d", 
                        repository, len(commits))
            
            return result
            
        except InvalidPayloadError:
            raise
        except Exception as e:
            logger.error("Unexpected error in parse_webhook_data: %s", str(e))
            raise InvalidPayloadError(f"Failed to parse webhook data: {str(e)}")

    def fetch_commit_diff(
        self, 
        repo_full_name: str, 
        commit_sha: str, 
        max_file_size: int = 1024 * 1024  # 1MB
    ) -> DiffData:
        """
        GitHub API를 통해 특정 커밋의 diff 정보를 가져오기
        """
        if not self.github_token:
            raise GitHubAPIError("GitHub token required for API access")
        
        try:
            url = f"https://api.github.com/repos/{repo_full_name}/commits/{commit_sha}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            logger.debug("Fetching commit diff from GitHub API: %s", url)
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 404:
                raise CommitNotFoundError(f"Commit {commit_sha} not found in {repo_full_name}")
            elif response.status_code == 403:
                raise RateLimitExceededError("GitHub API rate limit exceeded")
            elif response.status_code != 200:
                raise GitHubAPIError(f"GitHub API error: {response.status_code}")
            
            data = response.json()
            
            # Files 정보 파싱
            files_data = data.get("files", [])
            file_changes: List[FileChange] = []
            
            total_additions = 0
            total_deletions = 0
            
            for file_data in files_data:
                try:
                    # 파일 크기 체크
                    if file_data.get("changes", 0) > max_file_size:
                        logger.warning("File %s too large, skipping", file_data.get("filename"))
                        continue
                    
                    file_change = FileChange(
                        filename=file_data.get("filename", ""),
                        status=file_data.get("status", "modified"),
                        additions=file_data.get("additions", 0),
                        deletions=file_data.get("deletions", 0),
                        changes=file_data.get("changes", 0),
                        patch=file_data.get("patch", "")
                    )
                    file_changes.append(file_change)
                    
                    total_additions += file_change.additions
                    total_deletions += file_change.deletions
                    
                except Exception as e:
                    logger.warning("Failed to parse file change: %s", str(e))
                    continue
            
            # DiffData 생성
            diff_data = DiffData(
                commit_sha=commit_sha,
                total_additions=total_additions,
                total_deletions=total_deletions,
                file_changes=file_changes,
                timestamp=datetime.utcnow()
            )
            
            logger.debug("Successfully fetched diff for commit %s: %d files changed", 
                        commit_sha, len(file_changes))
            
            return diff_data
            
        except requests.exceptions.Timeout:
            raise NetworkTimeoutError(f"Timeout fetching commit {commit_sha}")
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error fetching commit diff: %s", str(e))
            raise DiffParsingError(f"Failed to fetch commit diff: {str(e)}")
