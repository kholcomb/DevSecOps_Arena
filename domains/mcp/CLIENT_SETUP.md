# MCP Gateway - Client Configuration Reference

**Gateway URL**: `http://localhost:8900/mcp`

> **Note**: Setup instructions are displayed automatically when you deploy an MCP challenge.

---

## Claude Desktop Configuration

**Locate your config file:**

macOS/Linux: `~/Library/Application Support/Claude/claude_desktop_config.json`
Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Add this MCP server:**
```json
{
  "mcpServers": {
    "devsecops-arena": {
      "url": "http://localhost:8900/mcp",
      "transport": {
        "type": "http"
      }
    }
  }
}
```

**Then restart Claude Desktop** and ask "What MCP tools are available?" to verify.

---

## Other MCP Clients

For any MCP-compatible client that supports HTTP/SSE transport:

- **URL**: `http://localhost:8900/mcp`
- **Protocol**: MCP 2025-11-25 (or 2025-03-26)
- **Transport**: HTTP with Server-Sent Events (SSE)
- **Headers**: `MCP-Protocol-Version: 2025-11-25`

---

## Quick Reference

**Check gateway status:**
```bash
curl http://localhost:8900/health
```

**View active challenge:**
```bash
curl http://localhost:8900/status | jq '.routing'
```

**Switch challenges** (no client reconfiguration needed):
```bash
arena cleanup
arena deploy mcp/world-1-foundations/level-02-privilege-escalation
```

---

For detailed MCP protocol documentation, see: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
