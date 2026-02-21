# Memories - RAG Service for AI Agent Memory

## Overview

A living memory service that provides persistent, searchable memory for AI agents. Agents can store observations, preferences, facts, and context, then retrieve them semantically across agents, projects, and arbitrary scopes.

## Goals

- Cross-agent memory: any agent can store and retrieve memories
- Cross-project memory: memories can be scoped to projects or searched globally
- Personality-aware: different agent personalities (e.g. Rex, Engineer) can maintain distinct memories
- Freeform scoping: agents apply arbitrary key-value tags and filter however they need at query time
- Accessible to any AI tool or system that can execute shell commands

## Architecture

- **Interface**: CLI tool (`memory`) written in Python
- **Vector Store**: ChromaDB running as a server in Docker (handles persistence, indexing, concurrency)
- **Embedding Model**: ChromaDB default (all-MiniLM-L6-v2, local, free) - configurable later
- **Deployment**: Docker Compose for ChromaDB; CLI tool installed locally (e.g. via pip)

The CLI is a thin client that connects to the ChromaDB server and adds business logic (decay, versioning, duplicate detection, tag discovery) on top.

## Authentication & Trust

- Trusted network model - no API keys or auth tokens
- Agents self-identify via CLI flags (agent name, personality, etc.)
- ChromaDB runs on localhost / private network

## Memory Model

### Structure

Each memory consists of:
- **content**: The memory text (what the agent observed, learned, or was told)
- **tags**: Freeform key-value metadata pairs (e.g. `project: project-1`, `type: preference`, `agent: rex`)
- **decay_policy**: How the memory ages over time (see Decay Policies below)
- **version**: Auto-incremented version number (memories are append-only)
- **confidence**: Current confidence score (affected by decay and reinforcement)
- **created_at**: Timestamp of creation
- **updated_at**: Timestamp of latest version

### Scoping via Tags

- Tags are fully freeform key-value pairs - no predefined schema
- Agents apply whatever tags make sense at creation time
- At query time, agents construct filters using any combination of tags
- A discovery command allows agents to list available tag keys and their values

Example tag combinations:
- `project: project-1, type: architecture` - project-specific architecture decisions
- `type: preference` - user preferences across all projects
- `agent: rex, personality: casual` - personality-specific memories

### Decay Policies

Agents specify a decay policy when creating a memory. Policies control how confidence degrades over time:

- **stable**: No decay. For facts, preferences, and decisions that remain true until explicitly contradicted. Example: "User prefers Python for CLI tools"
- **contextual**: Decays over time. For observations and events tied to a moment. Example: "User seemed frustrated during today's code review"
- **reinforceable**: Decays slowly, but retrieval or explicit reinforcement resets the decay. Example: "Team uses conventional commits format"

Specific decay rates and thresholds are implementation details to be tuned later.

### Versioning

- Memories are **append-only** - updates create a new version rather than modifying in place
- Each version preserves the full content and tags at that point in time
- Search returns the **latest version** by default, plus a **version count**
- A separate command provides the full version history for a given memory

## Duplicate Detection

- On store, the CLI checks for **semantically similar** existing memories
- If a potential duplicate is found, the memory is **not stored** by default
- Instead, feedback is returned to the caller identifying the possible duplicate(s)
- The caller can then decide to:
  - Proceed with storing anyway (`--force` flag)
  - Update the existing memory with a new version
  - Discard the new memory

## CLI Interface

### Memory Operations

```
memory create <content> [--tag key=value ...] [--decay stable|contextual|reinforceable] [--force]
    Store a new memory with optional tags and decay policy.
    Returns duplicate warning if similar memory exists (use --force to override).

memory search <query> [--tag key=value ...] [--limit N] [--format json|text]
    Semantic search with optional tag filters.
    Returns latest version of each match with version count.

memory get <id> [--format json|text]
    Get a specific memory (latest version).

memory history <id>
    Get full version history for a memory.

memory reinforce <id>
    Explicitly reinforce a memory (reset decay for reinforceable memories).

memory update <id> <content> [--tag key=value ...]
    Append a new version to an existing memory.

memory delete <id>
    Soft-delete a memory.
```

### Discovery

```
memory tags
    List all tag keys in use.

memory tags <key>
    List all values for a given tag key.
```

### Service Management

```
memory status
    Check connection to ChromaDB and report service health.
```

### Output Formats

- Default output is human-readable text
- `--format json` flag on relevant commands for machine-parseable output (used by AI agents)

## Consumers

- Multiple AI tools and agents (Claude Code, GPT-based agents, custom bots)
- All interaction via CLI commands (agents use Bash tool to invoke)
- No human-facing UI in initial scope

## Non-Goals (for now)

- Authentication and access control
- Human-facing UI for browsing memories
- Multi-user tenancy (single user assumed initially)
- Horizontal scaling / clustering
- Backup and replication strategy
- HTTP API (can be added later if cross-machine access is needed)
