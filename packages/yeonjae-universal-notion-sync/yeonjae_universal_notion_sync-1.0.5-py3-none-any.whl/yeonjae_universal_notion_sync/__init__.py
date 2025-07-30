"""
Universal Notion Sync

Notion API와의 범용 동기화 엔진으로, 다양한 데이터 소스를 Notion과 연동할 수 있습니다.
페이지, 데이터베이스, 블록 등을 자동으로 생성/업데이트하며, 
관계 매핑과 설정 기반 동기화를 지원합니다.

이 모듈은 AI-driven Modular Design 원칙에 따라 설계되었으며,
다른 프로젝트에서도 독립적으로 사용할 수 있습니다.
"""

__version__ = "1.0.0"

# Core services
from .service import (
    NotionAPIClient,
    NotionContentProcessor,
    RelationDiscoveryEngine,
    UniversalNotionSyncEngine,
    ConfigurationManager
)

# Data models and configurations
from .models import (
    SyncStrategy,
    ContentFormat,
    RelationDiscoveryMode,
    NotionCredentials,
    NotionBlock,
    NotionPage,
    NotionDatabase,
    RelationMapping,
    SyncTarget,
    SyncConfiguration,
    SyncResult,
    BatchSyncResult
)

# Configuration utilities
from .config import NotionSyncConfig

# Task utilities (if available)
try:
    from .tasks import sync_notion_data
    _TASKS_AVAILABLE = True
except ImportError:
    _TASKS_AVAILABLE = False
    sync_notion_data = None

__all__ = [
    '__version__',
    # Core services
    'NotionAPIClient',
    'NotionContentProcessor', 
    'RelationDiscoveryEngine',
    'UniversalNotionSyncEngine',
    'ConfigurationManager',
    # Data models
    'SyncStrategy',
    'ContentFormat',
    'RelationDiscoveryMode',
    'NotionCredentials',
    'NotionBlock',
    'NotionPage',
    'NotionDatabase',
    'RelationMapping',
    'SyncTarget',
    'SyncConfiguration',
    'SyncResult',
    'BatchSyncResult',
    # Configuration
    'NotionSyncConfig',
    # Tasks (optional)
    'sync_notion_data',
]
