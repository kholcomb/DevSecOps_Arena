# MCP Gateway - Client Configuration Reference

**Gateway URL**: `http://localhost:8900/mcp`

> **Note**: Setup instructions are displayed automatically when you deploy an MCP challenge.

---

## How to Connect Your AI Agent

### Option 1: Test with curl (Recommended for Validation)

The easiest way to test and interact with the MCP gateway:

```bash
# Check gateway is running
curl http://localhost:8900/health

# Initialize MCP session
curl -X POST http://localhost:8900/mcp \
  -H "MCP-Protocol-Version: 2025-11-25" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-11-25",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0"}
    }
  }'

# List available tools
curl -X POST http://localhost:8900/mcp \
  -H "MCP-Protocol-Version: 2025-11-25" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

### Option 2: MCP Inspector (Visual Testing)

Use the official MCP Inspector for a GUI-based testing experience:

```bash
npx @modelcontextprotocol/inspector http://localhost:8900/mcp
```

This opens a web interface where you can:
- Browse available tools
- Execute tool calls
- View responses
- Debug MCP interactions

**Website**: https://github.com/modelcontextprotocol/inspector

---

## Claude Desktop Integration

**Current Status**: Claude Desktop primarily supports stdio-based MCP servers, not direct HTTP.

**For stdio-based connection**, you would need an adapter script that:
1. Accepts stdin/stdout communication from Claude Desktop
2. Forwards requests to `http://localhost:8900/mcp` via HTTP
3. Returns responses back via stdout

**Note**: Native HTTP support in Claude Desktop is planned but not yet widely available. Check Claude Desktop release notes for updates.

---

## For MCP Client Developers

If you're building an MCP client or using a client that supports HTTP transport:

- **URL**: `http://localhost:8900/mcp`
- **Protocol**: MCP 2025-11-25 (fallback to 2025-03-26)
- **Transport**: HTTP with Server-Sent Events (SSE)
- **Required Headers**:
  - `MCP-Protocol-Version: 2025-11-25`
  - `Content-Type: application/json`
- **Session Management**: Use `MCP-Session-Id` header (provided by gateway)

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
