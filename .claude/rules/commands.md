# Commands & Workflows

## Local Environment

```bash
# Activate virtual environment (already exists at .venv/)
source .venv/bin/activate

# Install pytoyoda for development
pip install "pytoyoda>=4.0.0"
```

## Installing in Home Assistant

Copy the integration directory into the HA custom_components folder:

```bash
cp -r mytoyota/ /config/custom_components/toyota_custom/
```

Then restart Home Assistant and add the integration via Settings → Integrations → "+ Add" → "Toyota Connected Services (Custom)".

The domain name in `manifest.json` determines the folder name under `custom_components/`.

## No Test Suite

There are **no automated tests** in this repository. No `pytest`, no `tox`, no CI pipeline.
Testing is done manually by installing the integration in a Home Assistant instance.

Do not assume or generate test infrastructure unless explicitly asked.

## No Lint/Format Config

There is no `pyproject.toml`, `.flake8`, `ruff.toml`, or `pre-commit` config.
Follow the implicit style described in `style.md` and use `# noqa: RULE` inline suppressions where needed.

## Git

- Remote: `git@github.com:yabzec/myhatoyota.git`
- Main branch: `main`
- No CI/CD workflows configured

## Manifest Fields to Keep in Sync

When renaming or versioning, update `manifest.json` fields:

```json
{
  "domain": "myhatoyota",
  "name": "MyToyota Home Assistant",
  "requirements": ["pytoyoda>=4.0.0"],
  "version": "1.0.0"
}
```

The `domain` value must match the folder name under `custom_components/`.
