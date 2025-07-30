# Universal Notion Sync

Universal synchronization engine for seamless Notion API integration.

## Features

- **Universal Sync Engine**: Automatically sync data between any source and Notion
- **Smart Mapping**: Intelligent field mapping and type conversion
- **Relation Discovery**: Automatic discovery and management of database relations
- **Multi-Strategy Sync**: Support for various synchronization strategies
- **Configuration-Driven**: JSON-based configuration for flexible setups
- **Batch Processing**: Efficient batch operations for large datasets
- **Error Handling**: Robust error handling and retry mechanisms
- **Type Safety**: Complete type annotations with Pydantic models
- **Async Support**: Optional async operations for high-performance scenarios

## Installation

```bash
# Basic installation
pip install universal-notion-sync

# With async support
pip install universal-notion-sync[async]

# With validation features
pip install universal-notion-sync[validation]

# With Celery task support
pip install universal-notion-sync[celery]

# With all features
pip install universal-notion-sync[all]
```

## Quick Start

### Basic Notion Sync

```python
from universal_notion_sync import (
    UniversalNotionSyncEngine, 
    NotionCredentials,
    SyncConfiguration,
    SyncTarget
)

# Initialize with credentials
credentials = NotionCredentials(
    integration_token="your_notion_integration_token"
)

# Configure sync target
sync_config = SyncConfiguration(
    strategy="UPSERT",
    content_format="RICH_TEXT",
    relation_discovery_mode="AUTO"
)

sync_target = SyncTarget(
    database_id="your_database_id",
    configuration=sync_config
)

# Create sync engine
engine = UniversalNotionSyncEngine(credentials=credentials)

# Sync data
data = [
    {
        "title": "Project Alpha",
        "status": "In Progress", 
        "priority": "High",
        "tags": ["development", "urgent"]
    },
    {
        "title": "Project Beta",
        "status": "Planning",
        "priority": "Medium",
        "tags": ["research"]
    }
]

result = engine.sync_to_target(sync_target, data)
print(f"Synced {result.successful_items} items successfully")
```

### Advanced Configuration

```python
from universal_notion_sync import (
    ConfigurationManager,
    RelationMapping,
    SyncStrategy
)

# Load configuration from file
config_manager = ConfigurationManager()
config = config_manager.load_from_file("notion_sync_config.json")

# Custom relation mapping
relation_mapping = RelationMapping(
    source_field="user_id",
    target_property="assignee",
    relation_database_id="users_database_id",
    match_property="user_id"
)

# Advanced sync with custom mapping
engine = UniversalNotionSyncEngine(
    credentials=credentials,
    relation_mappings=[relation_mapping]
)

# Batch sync with custom strategy
batch_result = engine.batch_sync([
    (sync_target_1, data_1),
    (sync_target_2, data_2)
], strategy=SyncStrategy.CREATE_ONLY)

for target_result in batch_result.results:
    print(f"Target: {target_result.target_id}")
    print(f"Success: {target_result.successful_items}")
    print(f"Errors: {len(target_result.errors)}")
```

### Content Processing

```python
from universal_notion_sync import NotionContentProcessor, ContentFormat

processor = NotionContentProcessor()

# Convert markdown to Notion blocks
markdown_content = """
# Project Report

## Overview
This is a **comprehensive** report on project progress.

### Tasks
- [x] Design phase completed
- [ ] Development in progress  
- [ ] Testing pending

[Link to documentation](https://example.com/docs)
"""

notion_blocks = processor.convert_content(
    content=markdown_content,
    source_format=ContentFormat.MARKDOWN,
    target_format=ContentFormat.NOTION_BLOCKS
)

# Sync content to a page
page_result = engine.sync_to_page(
    page_id="your_page_id",
    blocks=notion_blocks
)
```

## Sync Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `CREATE_ONLY` | Only create new items | Initial data migration |
| `UPDATE_ONLY` | Only update existing items | Batch updates |
| `UPSERT` | Create or update items | General sync operations |
| `MIRROR` | Full synchronization | Complete data mirroring |

## Relation Discovery Modes

- `MANUAL`: Manually defined relations only
- `AUTO`: Automatic discovery based on field names
- `HYBRID`: Combination of manual and auto discovery

## Configuration File Format

```json
{
  "notion_credentials": {
    "integration_token": "${NOTION_TOKEN}"
  },
  "targets": [
    {
      "name": "projects_sync",
      "database_id": "database_id_here",
      "configuration": {
        "strategy": "UPSERT",
        "content_format": "RICH_TEXT",
        "relation_discovery_mode": "AUTO",
        "field_mappings": {
          "project_name": "title",
          "due_date": "deadline",
          "owner_id": "assignee"
        }
      }
    }
  ],
  "relation_mappings": [
    {
      "source_field": "owner_id",
      "target_property": "assignee", 
      "relation_database_id": "users_database_id",
      "match_property": "user_id"
    }
  ]
}
```

## Error Handling

The engine provides comprehensive error handling:

```python
try:
    result = engine.sync_to_target(sync_target, data)
    
    if result.errors:
        for error in result.errors:
            print(f"Error syncing item {error.item_index}: {error.message}")
            
except NotionAPIError as e:
    print(f"Notion API error: {e}")
except SyncConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Async Support

```python
import asyncio
from universal_notion_sync import AsyncUniversalNotionSyncEngine

async def async_sync_example():
    engine = AsyncUniversalNotionSyncEngine(credentials=credentials)
    
    result = await engine.async_sync_to_target(sync_target, data)
    return result

# Run async sync
result = asyncio.run(async_sync_example())
```

## License

MIT License
