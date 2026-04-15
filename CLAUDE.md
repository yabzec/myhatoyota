# mytoyota — Claude Guide

Home Assistant custom integration for Toyota vehicles via the `pytoyoda` library.
Domain: `myhatoyota` | Type: `cloud_polling` hub | Multi-vehicle support via one coordinator per VIN.

## Graph-First Rule

**Never hardcode or infer file/directory structure.** Always consult the graphify knowledge graph for physical layout, god nodes, and community structure:
- Quick query: `graphify-out/GRAPH_REPORT.md`
- Deep query: `/graphify query "<question>"`
- Update after structural changes: `/graphify . --update`

## Rule Files

@.claude/rules/architecture.md
@.claude/rules/commands.md
@.claude/rules/style.md
