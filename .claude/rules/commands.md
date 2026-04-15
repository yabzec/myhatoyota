# Commands & Workflow

## Environment

- Python 3.12, venv at `.venv/`
- Activate: `source .venv/bin/activate`
- Main dependency: `pytoyoda>=4.0.0`
- HA core installed in venv for IDE support and type checking

## Installing as a Custom Component

This integration is not packaged — deploy by copying the directory into HA's custom_components:

```bash
cp -r . <ha_config_dir>/custom_components/myhatoyota/
```

Then restart Home Assistant and add the integration via UI (Settings → Integrations → Add → "MyToyota Home Assistant").

## No Build Step

Pure Python, no compilation. No Makefile, no pyproject.toml. No test suite detected.

## Adding a New Entity

1. Add `value_fn` lambda to the description tuple in the relevant platform file.
2. Add `translation_key` entry to `strings.json` under the correct platform section.
3. Mirror the key in `translations/en.json` and `translations/it.json`.
4. `strings.json` and `translations/` must stay in sync — missing keys cause HA warnings.

## Translations

- `strings.json` — source of truth for HA frontend tooling
- `translations/en.json`, `translations/it.json` — runtime files loaded by HA
- Both must be updated together whenever a new `translation_key` is introduced

## Graphify

- First time or after structural changes: `/graphify .`
- Incremental update after file edits: `/graphify . --update`
- Query without rebuild: `/graphify query "<question>"`
