# Implementation Plan: Track 2 — MCP Server & Gemini CLI Extension

**Branch**: `008-mcp-gemini-extension` | **Date**: 2026-11-24 | **Spec**: [spec.md](spec.md)

## Summary
Expose First ADE's existing orchestrator and services over stdio via an `mcp` subcommand (`ade-compliance mcp`), add `--format gemini-hook` to `prime`, and ship a lightweight Gemini CLI extension manifest (`integrations/gemini-cli/`) that wires startup context injection and pre-commit verification.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: `mcp` (official Python SDK, optional extra `[mcp]`), `click`, `pydantic`  
**Storage**: Delegates to existing `DatabaseManager` / SQLite audit log  
**Testing**: `pytest` (stdio JSON-RPC roundtrip + Gemini hook JSON schema validation)  
**Dependencies**: Builds on `004-prime-agent` and `006-sdd-ddd-adapters` (`conductor` provider)

## Constitution Check
- **Architectural Constraints (V)**: MCP server and Gemini hook are thin transport adapters over `ComplianceOrchestrator` and `BaseService` subclasses—zero duplicated business logic.
- **AI Collaboration (VI)**: Directly operationalizes `Σ.5` (Human-AI Symbiosis) inside Gemini CLI.

## Project Structure
```text
src/ade_compliance/
├── cli.py                 # Add `mcp` command & `--format gemini-hook`
└── mcp_server.py          # Thin stdio MCP tool adapter

integrations/gemini-cli/
├── gemini-extension.json  # Gemini CLI extension manifest
└── hooks.json             # Startup/resume hook invoking `ade-compliance prime`

tests/unit/
├── test_mcp_server.py
└── test_gemini_hook.py
```
