# Universal Git Data Parser

Universal Git webhook data parser supporting GitHub, GitLab, and other SCM platforms.

## Features

- **Multi-Platform Support**: GitHub, GitLab, Bitbucket webhook parsing
- **Data Validation**: Comprehensive validation of webhook payloads
- **Structured Output**: Convert raw webhooks to structured data models
- **Error Handling**: Robust error handling for malformed data
- **Type Safety**: Complete type annotations with Pydantic models
- **Extensible**: Easy to add support for new SCM platforms
- **Performance**: Optimized parsing for high-throughput scenarios

## Installation

```bash
# Basic installation
pip install universal-git-data-parser

# With GitHub support
pip install universal-git-data-parser[github]

# With GitLab support  
pip install universal-git-data-parser[gitlab]

# With validation features
pip install universal-git-data-parser[validation]

# With all features
pip install universal-git-data-parser[all]
```

## Quick Start

### GitHub Webhook Parsing

```python
from universal_git_data_parser import GitDataParserService

# Initialize parser
parser = GitDataParserService()

# Parse GitHub push webhook
headers = {"X-GitHub-Event": "push"}
payload = {
    "repository": {"name": "my-repo", "full_name": "user/my-repo"},
    "ref": "refs/heads/main",
    "commits": [
        {
            "id": "abc123",
            "message": "Fix bug in parser",
            "author": {"name": "Developer", "email": "dev@example.com"},
            "timestamp": "2024-01-01T12:00:00Z",
            "added": ["file1.py"],
            "modified": ["file2.py"],
            "removed": []
        }
    ]
}

# Parse and validate
validated_event = parser.parse_github_push(headers, payload)

print(f"Repository: {validated_event.repository}")
print(f"Branch: {validated_event.ref}")
print(f"Commits: {len(validated_event.commits)}")
```

### Advanced Usage

```python
from universal_git_data_parser import (
    GitDataParserService, ValidatedEvent, CommitInfo
)

parser = GitDataParserService()

# Custom validation options
try:
    event = parser.parse_github_push(
        headers=headers,
        payload=payload,
        validate_signatures=True,
        strict_mode=True
    )
    
    # Access structured data
    for commit in event.commits:
        print(f"Commit: {commit.id}")
        print(f"Author: {commit.author}")
        print(f"Message: {commit.message}")
        print(f"Files changed: {len(commit.added + commit.modified + commit.removed)}")
        
except InvalidPayloadError as e:
    print(f"Invalid payload: {e}")
except UnsupportedPlatformError as e:
    print(f"Platform not supported: {e}")
```

## Supported Platforms

| Platform | Push Events | Pull Request | Issues | Tags |
|----------|-------------|--------------|--------|------|
| GitHub   | ✅ Full     | ✅ Full      | ⏳ Planned | ⏳ Planned |
| GitLab   | ✅ Basic    | ⏳ Planned   | ⏳ Planned | ⏳ Planned |
| Bitbucket| ⏳ Planned  | ⏳ Planned   | ⏳ Planned | ⏳ Planned |

## Data Models

The parser outputs structured Pydantic models:

- `ValidatedEvent`: Main event container
- `CommitInfo`: Individual commit information
- `DiffData`: File change details
- `Author`: Commit author information
- `FileChange`: File modification details

## Error Handling

Comprehensive exception hierarchy:

- `GitDataParserError`: Base exception
- `InvalidPayloadError`: Malformed webhook data
- `UnsupportedPlatformError`: Platform not supported
- `DiffParsingError`: Error parsing file changes
- `TimestampParsingError`: Invalid timestamp format

## License

MIT License
