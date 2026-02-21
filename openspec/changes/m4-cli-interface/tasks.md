## 1. Package Initialization

- [x] 1.1 Update `src/memories/__init__.py` — Import and instantiate Settings, ChromaDBAdapter, and MemoryService. Export the service instance and Typer app. Ensure ChromaDB connection is lazy (adapter connects on first use, not on import).

## 2. CLI Commands

- [x] 2.1 Rewrite `src/memories/cli.py` — Create Typer app. Implement `create` command: positional `content` arg, options `--agent`, `--personality`, `--project`, `--type`, `--global` (flag), `--decay` (choice: stable/contextual/reinforceable, default stable), `--format` (choice: json/text, default json). Build MemoryCreate from args, call service.create_memory(), output result.
- [x] 2.2 Implement `search` command in `cli.py`: positional `query` arg, options `--agent`, `--personality`, `--project`, `--type`, `--global` (flag), `--limit` (int, default 10), `--min-confidence` (float, default 0.3), `--format`. Call service.search_memories(), output SearchResponse.
- [x] 2.3 Implement `get` command in `cli.py`: positional `id` arg, `--format`. Call service.get_memory(), output MemoryResponse.
- [x] 2.4 Implement `reinforce` command in `cli.py`: positional `id` arg, `--format`. Call service.reinforce_memory(), output result.
- [x] 2.5 Implement `delete` command in `cli.py`: positional `id` arg, `--format`. Call service.delete_memory(), output result.
- [x] 2.6 Implement `status` command in `cli.py`: `--format` only. Call service.get_status(), output health status.

## 3. Output Formatting

- [x] 3.1 Implement output helper functions in `cli.py` (or a small `output.py` module): `output_json(data: dict, file=sys.stdout)` using json.dumps with indent=2, and `output_text(data: dict, file=sys.stdout)` with simple key-value formatting.

## 4. Error Handling

- [x] 4.1 Add try/except to every command in `cli.py`: catch MemoryNotFoundError, InvalidOperationError, and general exceptions (ChromaDB connection failures). Write JSON error to stderr, raise typer.Exit(code=1).

## 5. End-to-End Verification

- [x] 5.1 Manually verify all 6 commands against a running ChromaDB instance: create a memory, search for it, get it by ID, reinforce it (reinforceable policy), delete it, check status. Verify JSON output and exit codes. *(Requires running ChromaDB)*
