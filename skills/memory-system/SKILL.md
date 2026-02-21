---
name: memory-system
description: >-
  Persistent memory system for AI agents. Stores, searches, and manages
  memories across sessions using semantic vector search. Use this skill when
  an agent needs to remember something for later, recall past context,
  search for previously stored knowledge, check what memories exist,
  reinforce important memories, or delete outdated ones. Trigger on:
  remember, recall, forget, memory, memories, "what do you know about",
  "store this for later", "do you remember".
license: MIT
metadata:
  author: memories
  version: "1.1"
---

Persistent, semantically-searchable memory store for AI agents.

## Why use persistent memory

- **Continuity across sessions** — context survives session boundaries; no re-explaining needed.
- **Semantic recall** — search by meaning, not exact keywords. "greeting style" finds "Always sign off with Peace, my dude."
- **Controlled forgetting** — decay policies expire stale memories automatically so the store stays relevant.
- **Scoped organization** — metadata filters (`--agent`, `--project`, `--type`) keep memories cleanly separated.

## Commands

### status

```bash
memory status
```

Returns `{ status, host, collection, count }`. Use this to check health and see how many memories exist.

### create

```bash
memory create "Always sign off messages with Peace, my dude" \
  --agent claude --type preference --decay stable
```

Returns the full stored memory object (id, content, metadata, timestamps).

| Option | Description | Default |
|---|---|---|
| `--agent` | Who this memory belongs to (e.g. `claude`) | `""` |
| `--personality` | Personality context | `""` |
| `--project` | Project scope | `""` |
| `--type` | Free-form category (e.g. `preference`, `fact`, `instruction`) | `""` |
| `--global` | Flag — mark as globally relevant (no value) | `false` |
| `--decay` | Decay policy: `stable`, `contextual`, `reinforceable` | `stable` |

### search

```bash
memory search "sign off greeting" --limit 5
```

Returns `{ results: [...], count }`. Results are ranked by semantic similarity, not keyword match.

| Option | Description | Default |
|---|---|---|
| `--agent` | Filter by agent | `""` |
| `--personality` | Filter by personality | `""` |
| `--project` | Filter by project | `""` |
| `--type` | Filter by memory type | `""` |
| `--global` | Flag — only return global memories | `false` |
| `--limit` | Max results | `10` |
| `--min-confidence` | Minimum confidence threshold (0.0–1.0) | `0.3` |

### get

```bash
memory get <uuid>
```

Returns the full memory object by ID.

### reinforce

```bash
memory reinforce <uuid>
```

Resets the decay timer on a `reinforceable` memory, restoring confidence to ~1.0. Returns `{ id, confidence, last_reinforced_at }`. Only works on memories with `reinforceable` decay policy.

### delete

```bash
memory delete <uuid>
```

Soft-deletes a memory. It is excluded from future searches but not destroyed. Returns `{ id, deleted }`.

## Decay policies

| Policy | Behavior | Use for |
|---|---|---|
| `stable` | Never decays — confidence stays at 1.0 forever | Permanent facts, preferences, instructions |
| `contextual` | Fades to 0 over 30 days | Session-specific or temporary context |
| `reinforceable` | Fades over 30 days but resets on `reinforce` | Knowledge that matters while actively used |

## Output format

All commands default to `--format json`. Pass `--format text` for human-readable output. Errors go to stderr as JSON with an `error` key and exit code 1.

## Workflows

**Remember something new** — search first to avoid duplicates, then store:
```bash
memory search "the thing to remember" --limit 3
memory create "the thing to remember" --decay stable --type instruction
```

**Recall past context** — search by meaning, not exact words:
```bash
memory search "topic they're asking about" --limit 10
```

**Clean up outdated memories** — search to find candidates, then delete by ID:
```bash
memory search "outdated topic" --limit 20 --min-confidence 0.0
memory delete <uuid>
```

## Guardrails

- Search before creating to avoid duplicates.
- Never store sensitive data (passwords, tokens, secrets).
- Use `--decay stable` for permanent preferences and instructions.
- Use metadata filters (`--agent`, `--project`, `--type`) to keep memories organized.
- Confirm with the user before deleting memories.
