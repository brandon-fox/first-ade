# Tasks: Track 2 — MCP Server & Gemini CLI Extension

**Input**: Design documents from `/specs/008-mcp-gemini-extension/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required)

## Phase 1: Tests First (TDD)
- [ ] T001 [US1] [FR-001] Write stdio JSON-RPC roundtrip tests for `ade_check`, `ade_attest`, `ade_prime`, and `ade_traceability` in `tests/unit/test_mcp_server.py`
- [ ] T002 [US2] [FR-002] Write unit tests for `ade-compliance prime --format gemini-hook` output schema in `tests/unit/test_gemini_hook.py`

## Phase 2: Implementation
- [ ] T003 [US1] [FR-001] Implement stdio MCP adapter and `ade-compliance mcp` command in `src/ade_compliance/mcp_server.py` and `src/ade_compliance/cli.py`
- [ ] T004 [US2] [FR-002] [FR-003] Add `--format gemini-hook` output mode and Gemini CLI extension manifest in `integrations/gemini-cli/gemini-extension.json` and `integrations/gemini-cli/hooks.json`
