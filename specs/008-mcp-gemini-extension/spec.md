# Feature Specification: Track 2 — MCP Server & Gemini CLI Extension

**Feature Branch**: `008-mcp-gemini-extension`  
**Created**: 2026-11-24  
**Status**: Draft (Proposed)  
**Input**: Product strategy alignment (Track 2) — wrap the standalone compliance gate as an MCP server and package a Gemini CLI extension using lifecycle hooks to plug into Conductor and other coding agents.

## User Scenarios & Testing

### User Story 1 - Model Context Protocol (MCP) Compliance Server (Priority: P1)
As an AI coding agent (Gemini CLI, Claude Code, Cursor), I want to call First ADE's `check`, `attest`, and `prime` capabilities as native MCP tools over stdio so I can self-verify compliance without shelling out to raw HTTP endpoints.

**Why this priority**: Makes First ADE natively consumable by every modern MCP-compatible coding agent.

**Independent Test**: Start `ade-compliance mcp` over stdio, send a JSON-RPC `tools/list` and `tools/call` (`ade_check`) request, and verify structured violation output is returned.

**Acceptance Scenarios**:
1. **Given** an MCP client connects to `ade-compliance mcp`, **When** it lists tools, **Then** `ade_check`, `ade_attest`, `ade_prime`, and `ade_traceability` are exposed with JSON schemas.
2. **Given** an agent invokes `ade_check` on modified files, **When** violations exist, **Then** it returns structured violations with axiom IDs (`Π.x.y`) and remediation hints.

---

### User Story 2 - Gemini CLI Extension & Lifecycle Hooks (Priority: P2)
As a Gemini CLI user (including Conductor users), I want a First ADE extension that automatically primes my session on `startup`/`resume` and runs compliance reconciliation before commits so I get constitutional guardrails without manual prompting.

**Why this priority**: Captures the Gemini CLI + Conductor ecosystem with zero-friction hook integration.

**Independent Test**: Load the extension manifest and invoke the startup hook script; verify it outputs valid Gemini CLI `hookSpecificOutput.additionalContext` JSON containing active axioms and staged-file constraints.

**Acceptance Scenarios**:
1. **Given** the Gemini CLI extension is installed, **When** a session starts (`startup`/`resume`), **Then** the hook runs `ade-compliance prime --format gemini-hook` and injects active constraints into `additionalContext`.
2. **Given** Conductor generates a plan/spec, **When** implementation is staged, **Then** First ADE's `conductor` spec provider validates spec existence and test alignment.

---

### Edge Cases
- `ade-compliance` not yet initialized in repo: startup hook returns advisory `systemMessage` suggesting `ade-compliance init` rather than crashing the Gemini CLI session.
- MCP server timeout: enforce fast heuristic execution (`<500ms`) so agent tool calls remain snappy.

## Requirements

### Functional Requirements
- **FR-001**: CLI MUST expose `ade-compliance mcp` running an MCP stdio server wrapping `ComplianceOrchestrator`, `AttestService`, and `PrimeService`.
- **FR-002**: `ade-compliance prime` MUST support `--format gemini-hook` outputting Gemini CLI `hookSpecificOutput.additionalContext` JSON.
- **FR-003**: Repository MUST include a Gemini CLI extension manifest (`gemini-extension.json` + hook configuration) ready for `gemini extensions install`.
