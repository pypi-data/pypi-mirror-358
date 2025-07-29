#\!/bin/bash

echo "Searching for Claude logs..."

# Common log locations
POSSIBLE_PATHS=(
    "$HOME/Library/Logs/Claude"
    "$HOME/Library/Application Support/Claude/logs"
    "$HOME/.config/Claude/logs"
    "$HOME/Library/Logs/com.anthropic.claude"
    "/var/log/claude"
)

for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "✅ Found Claude logs at: $path"
        echo "Recent log files:"
        ls -la "$path" | tail -10
        echo ""
    fi
done

# Check for Claude config
CONFIG_PATHS=(
    "$HOME/Library/Application Support/Claude/claude_config.json"
    "$HOME/.config/Claude/config.json"
    "$HOME/.claude/config.json"
)

for path in "${CONFIG_PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo "✅ Found Claude config at: $path"
        echo "MCP servers configured:"
        grep -A 5 "mcpServers" "$path" 2>/dev/null | head -20
        echo ""
    fi
done
