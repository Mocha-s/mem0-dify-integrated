# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Dify plugin for mem0, a memory management system that enables conversation history storage and retrieval for LLM applications. The plugin provides four core tools:
1. `add_memory` - Stores conversation history and context for users
2. `retrieve_memory` - Retrieves relevant conversation history based on queries
3. `delete_memory` - Deletes specific memories or all memories for a user
4. `update_memory` - Updates existing memories

## Architecture

The plugin follows a standard Dify plugin structure with:
- `main.py` - Entry point that initializes and runs the plugin
- `provider/mem0.py` - Tool provider that validates credentials
- `tools/` directory containing:
  - `add_memory.py` - Implementation for adding memories
  - `retrieve_memory.py` - Implementation for retrieving memories
  - `delete_memory.py` - Implementation for deleting memories
  - `update_memory.py` - Implementation for updating memories
- YAML files defining tool interfaces and plugin metadata

## Development Commands

- Install dependencies: `pip install -r requirements.txt`
- Run the plugin locally: `python main.py`
- The plugin communicates with the mem0 API via HTTP requests
- Credentials required: `mem0_api_key` (and optionally `mem0_api_url`)

## Key Files to Modify

- `tools/add_memory.py` - For changes to memory addition logic
- `tools/retrieve_memory.py` - For changes to memory retrieval logic
- `tools/delete_memory.py` - For changes to memory deletion logic
- `tools/update_memory.py` - For changes to memory update logic
- `provider/mem0.py` - For credential validation changes
- `manifest.yaml` - For plugin metadata changes

## Enhanced Functionality

The plugin now supports all core mem0 memory operations:
- Add memories using the v1 API endpoint
- Retrieve memories using the v1 search endpoint (with support for v2 search parameters)
- Delete specific memories or all memories for a user using the v1 delete endpoint
- Update existing memories using the v1 update endpoint

The implementation includes proper error handling, logging, and response processing for all operations.

## Dify Plugin Development Guidelines

This plugin follows Dify's plugin development guidelines:
- All tools are properly defined in YAML files with clear descriptions
- The plugin manifest follows Dify's schema requirements
- Tools have appropriate parameter validation and error handling
- The plugin provides multilingual support (en_US, zh_Hans, pt_BR, ja_JP)
- All tools return both JSON and text format responses for compatibility
- Proper resource allocation is defined in the manifest file