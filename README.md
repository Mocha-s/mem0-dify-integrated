## mem0

**Author:** yevanchen
**Version:** 0.0.1
**Type:** tool

### Description

mem0 is a memory management plugin that enables conversation history storage and retrieval for LLM applications.

![workflow](./_assets/workflow.png)


### Setup

1. Get your API key from [mem0 dashboard](https://app.mem0.ai/dashboard/api-keys)
2. Install the package:
```bash
pip install mem0ai
```

3. Initialize the client:
```python
from mem0 import MemoryClient
client = MemoryClient(api_key="your-api-key")
```

![dashboard](./_assets/dashboard.png)

### Configuration

#### API Key
Required for authentication with the mem0 API.

#### API URL (Optional)
You can specify a custom API URL if you're using a self-hosted instance or a different endpoint:
- Default: `https://api.mem0.ai`
- Format: Enter the base URL without trailing slash (e.g., `https://your-custom-api.example.com`)

### Memory Actions

#### add_memory
Stores conversation history and context for users.

```python
messages = [
    {"role": "user", "content": "Hi, I'm Alex. I'm a vegetarian and I'm allergic to nuts."},
    {"role": "assistant", "content": "Hello Alex! I've noted your dietary preferences."}
]
client.add(messages, user_id="alex")
```

Backend logic:
- Messages are stored in user-specific partitions using `user_id`
- Supports conversation history and context storage
- Handles message format validation and processing
- Optimizes storage for efficient retrieval

#### retrieve_memory
Retrieves relevant conversation history based on queries.

```python
query = "What can I cook for dinner tonight?"
memories = client.search(query, user_id="alex")
```

Backend logic:
- Semantic search across user's memory partition
- Returns relevant conversation snippets
- Handles context ranking and relevance scoring
- Optimizes query performance
- Supports both V1 and V2 search APIs with advanced filtering options

#### update_memory
Updates existing memories with new content.

```python
client.update(memory_id="memory-123", memory="Updated content", user_id="alex")
```

Backend logic:
- Updates specific memory by ID
- Supports updating content, categories, and metadata
- Maintains memory relationships and context

#### delete_memory
Deletes specific memories or all memories for a user.

```python
# Delete specific memory
client.delete(memory_id="memory-123")

# Delete all memories for a user
client.delete_all(user_id="alex")
```

Backend logic:
- Supports deletion of individual memories by ID
- Supports bulk deletion of all memories for a user
- Handles proper cleanup of memory relationships

### Usage in Dify

1. In Dify workflows, place `retrieve_memory` before LLM calls to provide context
2. Add `add_memory` after LLM responses to store new interactions
3. Use `update_memory` to modify existing memories when needed
4. Use `delete_memory` to remove outdated or irrelevant memories
5. `user_id` can be customized in workflow run API
6. Note: iframe and webapp modes currently don't support user_id due to lack of access control

### Advanced Features

#### V2 Search API
The retrieve_memory tool now supports the mem0 V2 search API with advanced filtering capabilities:
- Complex logical operations (AND, OR, NOT)
- Comparison operators for numerical and date fields
- Advanced filtering by categories, metadata, and other attributes
- Pagination support with limit and offset parameters

#### Enhanced Memory Operations
All four core memory operations (add, retrieve, update, delete) are now supported:
- Full CRUD functionality for memory management
- Consistent error handling and response formatting
- Detailed logging for debugging and monitoring

### Maybe Future Features
- Multimodal Support
- Memory Customization
- Custom Categories & Instructions
- Direct Import
- Async Client
- Memory Export
- Webhooks
- Graph Memory
- REST API Server
- OpenAI Compatibility
- Custom Prompts