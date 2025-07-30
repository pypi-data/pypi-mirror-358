"""Basic tests for universal-notion-sync package."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from enum import Enum

import universal_notion_sync


def test_package_version():
    """Test package version is accessible."""
    assert hasattr(universal_notion_sync, '__version__')
    assert universal_notion_sync.__version__ == "1.0.0"


def test_package_imports():
    """Test main imports are available."""
    # Core services
    assert hasattr(universal_notion_sync, 'UniversalNotionSyncEngine')
    assert hasattr(universal_notion_sync, 'NotionAPIClient')
    assert hasattr(universal_notion_sync, 'NotionContentProcessor')
    assert hasattr(universal_notion_sync, 'RelationDiscoveryEngine')
    assert hasattr(universal_notion_sync, 'ConfigurationManager')
    
    # Models
    assert hasattr(universal_notion_sync, 'NotionCredentials')
    assert hasattr(universal_notion_sync, 'SyncTarget')
    assert hasattr(universal_notion_sync, 'SyncConfiguration')
    assert hasattr(universal_notion_sync, 'SyncResult')
    assert hasattr(universal_notion_sync, 'BatchSyncResult')
    
    # Enums
    assert hasattr(universal_notion_sync, 'SyncStrategy')
    assert hasattr(universal_notion_sync, 'ContentFormat')
    assert hasattr(universal_notion_sync, 'RelationDiscoveryMode')


def test_sync_strategy_enum():
    """Test SyncStrategy enum values."""
    from universal_notion_sync import SyncStrategy
    
    assert isinstance(SyncStrategy.FULL_SYNC, SyncStrategy)
    assert isinstance(SyncStrategy.INCREMENTAL, SyncStrategy)
    assert isinstance(SyncStrategy.MANUAL, SyncStrategy)


def test_content_format_enum():
    """Test ContentFormat enum values."""
    from universal_notion_sync import ContentFormat
    
    assert isinstance(ContentFormat.MARKDOWN, ContentFormat)
    assert isinstance(ContentFormat.JSON, ContentFormat)


def test_relation_discovery_mode_enum():
    """Test RelationDiscoveryMode enum values."""
    from universal_notion_sync import RelationDiscoveryMode
    
    assert isinstance(RelationDiscoveryMode.DISABLED, RelationDiscoveryMode)
    assert isinstance(RelationDiscoveryMode.SHALLOW, RelationDiscoveryMode)
    assert isinstance(RelationDiscoveryMode.DEEP, RelationDiscoveryMode)
    assert isinstance(RelationDiscoveryMode.CUSTOM, RelationDiscoveryMode)


def test_notion_credentials_model():
    """Test NotionCredentials model creation."""
    from universal_notion_sync import NotionCredentials
    
    credentials = NotionCredentials(
        token="secret_token_123",
        version="2022-06-28"
    )
    
    assert credentials.token == "secret_token_123"
    assert credentials.version == "2022-06-28"


def test_sync_configuration_model():
    """Test SyncConfiguration model creation."""
    from universal_notion_sync import SyncConfiguration, NotionCredentials, RelationDiscoveryMode
    
    credentials = NotionCredentials(token="test_token")
    config = SyncConfiguration(
        credentials=credentials,
        relation_discovery=RelationDiscoveryMode.SHALLOW,
        batch_size=50
    )
    
    assert config.credentials.token == "test_token"
    assert config.relation_discovery == RelationDiscoveryMode.SHALLOW
    assert config.batch_size == 50


def test_sync_target_model():
    """Test SyncTarget model creation."""
    from universal_notion_sync import SyncTarget, SyncStrategy, ContentFormat
    
    target = SyncTarget(
        id="db_123456",
        type="database",
        name="test_target",
        output_path="./output.md",
        format=ContentFormat.MARKDOWN,
        strategy=SyncStrategy.INCREMENTAL
    )
    
    assert target.id == "db_123456"
    assert target.type == "database"
    assert target.name == "test_target"
    assert target.output_path == "./output.md"
    assert target.format == ContentFormat.MARKDOWN
    assert target.strategy == SyncStrategy.INCREMENTAL


def test_notion_api_client_creation():
    """Test NotionAPIClient instantiation."""
    from universal_notion_sync import NotionAPIClient, NotionCredentials
    
    credentials = NotionCredentials(token="test_token")
    client = NotionAPIClient(credentials=credentials)
    
    assert client.credentials.token == "test_token"
    assert hasattr(client, 'get_database')
    assert hasattr(client, 'query_database')
    assert hasattr(client, 'get_page')
    assert hasattr(client, 'get_block_children')


def test_notion_content_processor_creation():
    """Test NotionContentProcessor instantiation."""
    from universal_notion_sync import NotionContentProcessor, NotionAPIClient, NotionCredentials
    
    credentials = NotionCredentials(token="test_token")
    api_client = NotionAPIClient(credentials=credentials)
    processor = NotionContentProcessor(api_client=api_client)
    
    assert hasattr(processor, 'process_page')
    assert hasattr(processor, 'process_database')
    assert processor.api_client == api_client


def test_relation_discovery_engine_creation():
    """Test RelationDiscoveryEngine instantiation."""
    from universal_notion_sync import RelationDiscoveryEngine, NotionAPIClient, NotionContentProcessor, NotionCredentials
    
    credentials = NotionCredentials(token="test_token")
    api_client = NotionAPIClient(credentials=credentials)
    processor = NotionContentProcessor(api_client=api_client)
    engine = RelationDiscoveryEngine(api_client=api_client, processor=processor)
    
    assert hasattr(engine, 'discover_hierarchy')
    assert engine.api_client == api_client
    assert engine.processor == processor


def test_universal_notion_sync_engine_creation():
    """Test UniversalNotionSyncEngine instantiation."""
    from universal_notion_sync import UniversalNotionSyncEngine, SyncConfiguration, NotionCredentials
    
    credentials = NotionCredentials(token="test_token")
    config = SyncConfiguration(credentials=credentials)
    engine = UniversalNotionSyncEngine(config=config)
    
    assert engine.config.credentials.token == "test_token"
    assert hasattr(engine, 'sync_target')
    assert hasattr(engine, 'sync_all_targets')
    assert hasattr(engine, 'discover_and_add_hierarchy')


def test_configuration_manager_creation():
    """Test ConfigurationManager instantiation."""
    from universal_notion_sync import ConfigurationManager
    
    manager = ConfigurationManager()
    
    # Check if it has the actual methods from the implementation
    assert hasattr(manager, 'load_configuration')


def test_notion_sync_config_creation():
    """Test NotionSyncConfig instantiation."""
    from universal_notion_sync import NotionSyncConfig
    
    config = NotionSyncConfig()
    
    assert hasattr(config, 'load_config')
    assert hasattr(config, 'get_targets')
    assert hasattr(config, 'get_credentials')


def test_sync_result_model():
    """Test SyncResult model creation."""
    from universal_notion_sync import SyncResult
    
    # Check actual field names from the model
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=30)
    
    result = SyncResult(
        target_id="db_123",
        target_name="test_target",
        success=True,
        start_time=start_time,
        end_time=end_time,
        changes_detected=True,
        output_file="./output.md"
    )
    
    assert result.target_id == "db_123"
    assert result.target_name == "test_target"
    assert result.success is True
    assert result.changes_detected is True
    assert result.output_file == "./output.md"
    assert result.duration_seconds == 30.0


def test_batch_sync_result_model():
    """Test BatchSyncResult model creation."""
    from universal_notion_sync import BatchSyncResult, SyncResult
    
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=30)
    
    individual_result = SyncResult(
        target_id="db_123",
        target_name="test_target",
        success=True,
        start_time=start_time,
        end_time=end_time
    )
    
    batch_start_time = datetime.now()
    batch_end_time = batch_start_time + timedelta(seconds=60)
    
    batch_result = BatchSyncResult(
        batch_id="batch_123",
        start_time=batch_start_time,
        end_time=batch_end_time,
        total_targets=1,
        successful_syncs=1,
        failed_syncs=0,
        results=[individual_result]
    )
    
    assert len(batch_result.results) == 1
    assert batch_result.results[0].target_id == "db_123"
    assert batch_result.total_targets == 1
    assert batch_result.successful_syncs == 1
    assert batch_result.success_rate == 1.0


def test_tasks_import_optional():
    """Test that tasks import is optional."""
    # Tasks should be importable if celery is available
    try:
        from universal_notion_sync import sync_notion_data
        # If import succeeds, check it's callable or None
        assert sync_notion_data is None or callable(sync_notion_data)
    except ImportError:
        # Import error is acceptable if celery is not installed
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
