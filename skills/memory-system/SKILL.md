---
name: memory-system
description: Use the persistent memory system to store, search, and manage AI agent memories. Invoke when the user asks to remember something, recall a memory, check memory status, or manage stored memories.
license: MIT
metadata:
  author: memories
  version: "1.0"
---

Interact with the **memories** CLI — a persistent, semantically-searchable memory store backed by ChromaDB.

---

## Prerequisites

ChromaDB must be running in Docker. If commands fail with a connection error, tell the user:

```
ChromaDB isn't running. Start it with: docker compose up -d
```

The CLI is installed in the project virtualenv. **Always activate it before running commands:**

```bash
source /Users/robw-raviga/Developer/memories/.venv/bin/activate
```

---

## Commands

### Check status (count + health)

```bash
memory status
```

Returns: `{ status, host, collection, count }` — use this to see how many memories exist.

### Store a memory

```bash
memory create "Always sign off messages with Peace, my dude" \
  --agent claude \
  --type preference \
  --decay stable
```

**Key options:**
- `--agent` — who this memory belongs to (e.g. `claude`, `nigel`)
- `--personality` — personality context
- `--project` — project scope
- `--type` — free-form category (e.g. `preference`, `fact`, `instruction`)
- `--global` — mark as globally relevant (flag, no value)
- `--decay` — `stable` (never fades), `contextual` (fades over 30 days), `reinforceable` (fades but can be reset)

**Choosing decay policy:**
- `stable` — permanent facts, preferences, instructions
- `contextual` — session-specific or temporary context
- `reinforceable` — things that matter if actively used

### Search memories

```bash
memory search "sign off greeting" --limit 5
```

Searches by **semantic similarity** (not keyword match). Filter with `--agent`, `--personality`, `--project`, `--type`, `--global`, `--min-confidence`.

### Get a specific memory

```bash
memory get <uuid>
```

### Reinforce a memory (reset decay timer)

```bash
memory reinforce <uuid>
```

Only works for `reinforceable` decay policy. Resets confidence to ~1.0.

### Delete a memory (soft-delete)

```bash
memory delete <uuid>
```

Marks as deleted — excluded from future searches but not destroyed.

---

## Output format

All commands default to `--format json`. Add `--format text` for human-readable output.

Errors go to stderr as JSON with an `error` key and exit code 1.

---

## Common workflows

**User asks you to remember something:**
```bash
source .venv/bin/activate
memory create "the thing to remember" --decay stable --type instruction
```

**User asks what you remember:**
```bash
source .venv/bin/activate
memory search "topic they're asking about" --limit 10
```

**User asks how many memories / system health:**
```bash
source .venv/bin/activate
memory status
```

**User wants to clear test data:**
```bash
source .venv/bin/activate
# Search first to confirm what you're deleting
memory search "test" --limit 20 --min-confidence 0.0
# Then delete each by ID
memory delete <uuid>
```

There is no bulk-delete command. For mass cleanup, use Python directly:
```bash
source .venv/bin/activate && python3 -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
col = client.get_or_create_collection('memories')
result = col.get()
if result['ids']:
    col.delete(ids=result['ids'])
    print(f'Deleted {len(result[\"ids\"])} memories')
print(f'Remaining: {col.count()}')
"
```

---

## Guardrails

- **Always activate the venv** before running `memory` commands
- **Don't store sensitive data** (passwords, tokens, secrets)
- **Use `--decay stable`** for permanent preferences and instructions
- **Search before creating** to avoid duplicates
- **Confirm with the user** before bulk-deleting memories
