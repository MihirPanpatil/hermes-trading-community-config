# Hermes Trading Community Configuration

Sanitized export of the local Hermes setup used for the administrator-facing trading-community intelligence workflow.

## Included

- `hermes/config.yaml` — sanitized Hermes configuration and MCP registrations.
- `mcp/angel-one-mcp-server/` — read-only market-data MCP source, rate limiting, instrument validation, and tests.
- `mcp/exchange-rss-mcp/` — RSS aggregation MCP source with all-feed collection and per-feed failure isolation.

## Security

Secrets, credentials, local environment files, runtime logs, caches, compiled bytecode, and machine-specific state are intentionally excluded. Configure credentials through local environment variables; do not commit them.

The Angel One MCP must remain read-only. It must not be used to place, modify, or cancel orders without explicit authorization.

## Local setup

1. Create the required local environment files outside this repository.
2. Install each MCP according to its project documentation.
3. Adjust absolute paths in `hermes/config.yaml` for the target machine.
4. Run `hermes config check`.
5. Start the MCPs through Hermes and verify tool discovery with read-only smoke tests.

The broker movers endpoint reports derivatives movers (`PercPriceGainers`, `PercPriceLosers`, `PercOIGainers`, `PercOILosers`), not cash-equity breadth.
