# Commands & Workflow

## Environment

- Python 3.12, venv at `.venv/`
- Activate: `source .venv/bin/activate`
- pytoyoda is **vendored** in `_vendor/pytoyoda/` — do NOT install from PyPI
- HA core installed in venv for IDE support and type checking

## Deployment

HA runs on a separate machine. Deploy via git:

```bash
# On dev machine
git add -A && git commit -m "..." && git push

# On HA machine (in the integration directory)
git pull
# Then restart HA via UI or: ha core restart
```

The integration lives at `<ha_config>/custom_components/myhatoyota/`. HA picks up changes on restart.

## Vendored pytoyoda

`_vendor/pytoyoda/` contains a patched pytoyoda 4.2.0 committed to the repo. `__init__.py` injects it into `sys.path` at load time. To update the vendor copy after making fixes:

```bash
# Edit files directly in _vendor/pytoyoda/
# Then commit _vendor/ changes along with integration changes
```

`pytoyoda-src/` is a gitignored local dev clone — changes there are NOT deployed. Always edit `_vendor/pytoyoda/` for fixes that need to ship.

## No Build Step

Pure Python, no compilation. No Makefile, no pyproject.toml.

## Adding a New Entity

1. Add `value_fn` lambda to the description tuple in the relevant platform file.
2. Add `translation_key` entry to `strings.json` under the correct platform section.
3. Mirror the key in `translations/en.json` and `translations/it.json`.
4. `strings.json` and `translations/` must stay in sync — missing keys cause HA warnings.

## Translations

- `strings.json` — source of truth for HA frontend tooling
- `translations/en.json`, `translations/it.json` — runtime files loaded by HA
- Both must be updated together whenever a new `translation_key` is introduced

## API Inspection Tools

Located in `tools/`:

```bash
# Full inspection: parsed sensor values + raw endpoint JSON for all endpoints
python3 tools/inspect_api.py 2>/dev/null

# Raw status/trip_history dump (lower-level debugging)
python3 tools/investigate_status.py 2>/dev/null
```

Both load credentials from `.env` (`TOYOTA_EMAIL`, `TOYOTA_PASSWORD`). Useful for diagnosing why a sensor shows unknown or to verify what the Toyota API actually returns.

## Graphify

- First time or after structural changes: `/graphify .`
- Incremental update after file edits: `/graphify . --update`
- Query without rebuild: `/graphify query "<question>"`
