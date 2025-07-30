# Rongcloud Native MCP

RongCloud IM service based on MCP protocol (wrapping Rust SDK)

[中文文档](README.md)

## Usage

### Prerequisites - Install UV Package Manager

```bash
 pip install uv 
```

UV is a Python package installation and dependency management tool written in Rust, offering faster and more efficient experience than traditional tools (like pip). It focuses on two core objectives:

Speed: UV is optimized for package installation, dependency resolution, and virtual environment creation, providing significant performance improvements.
Efficiency: UV reduces resource consumption, especially in large projects.

The UVX command we'll use later means "download if not local, then run", and it runs in a separate virtual environment each time, making it ideal for large model/Agent-related scenarios.

### Using in Cursor (Similar for Cline / Claude)

Configuration path: Cursor -> Preferences -> Cursor Settings -> MCP -> Add new global MCP server
Configuration content:

```json
{
  "mcpServers": {
    "rongcloud-native-mcp-python": {
      "name": "rongcloud-native-mcp-python",
      "type": "stdio",
      "command": "uvx",
      "args": [
        "rongcloud-native-mcp-python"
      ],
      "env": {
          "APP_KEY": "Rongcloud App Key",
          "TOKEN": "Application SDK Token (obtained from Server API)",
          "AREA_CODE": "Data center region code, do not set for non-public cloud customers",
          "NAVI_URL": "Nav URL (for non-public cloud customers)",
          "STAT_URL": "Statistics URL (for non-public cloud customers)"
      }
    }
  }
}
```

### Environment Variables

- `APP_KEY`: (Required) Your Rongcloud application key
- `TOKEN`: (Required) Application SDK token, obtained from Server API
- `AREA_CODE`: (Optional) Data center region code:
  - 1: Beijing
  - 2: Singapore
  - 3: North America
  - 4: Singapore B
  - 5: Saudi Arabia
  - Note: Do not set for non-public cloud customers
- `NAVI_URL`: (Optional) Navigation URL, required for non-public cloud customers
- `STAT_URL`: (Optional) Statistics URL, required for non-public cloud customers

### Using in Cherry Studio

First install both UV and Bun (both required), then restart Cherry Studio. Configure as shown in the images below:
![Cherry Studio Interface Example](readme_img/cherry-studio-0.png)
![Cherry Studio Interface Example](readme_img/cherry-studio.png)

## Main Features and Tools Description (Continuously Updated)

The server exposes the following tools through the MCP protocol:

### 1. `send_private_text_message`

- **Function**: Send IM message to specified user (private chat)
- **Parameters**:
  - `user_id` (str, default ""): Message recipient's user ID
  - `content` (str, default ""): Message content
- **Returns**:
  - Failure: Dictionary containing `code` and `error`
  - Success: Dictionary containing `code`, `message_id` and `message`

### 2. `send_group_text_message`

- **Function**: Send IM message to specified group (group chat)
- **Parameters**:
  - `group_id` (str, default ""): Group ID
  - `content` (str, default ""): Message content
- **Returns**:
  - Failure: Dictionary containing `code` and `error`
  - Success: Dictionary containing `code`, `message_id` and `message`

### 3. `get_private_messages`

- **Function**: Get historical messages with specified user (private chat)
- **Parameters**:
  - `user_id` (str, default ""): User ID
  - `order_asc` (bool, default False): Sort order, False=descending, True=ascending
  - `count` (int, default 10): Number of messages to retrieve
- **Returns**:
  - Failure: Dictionary containing `code` and `error`
  - Success: Dictionary containing `code` and message array

### 4. `get_group_messages`

- **Function**: Get historical messages of specified group (group chat)
- **Parameters**:
  - `group_id` (str, default ""): Group ID
  - `order_asc` (bool, default False): Sort order, False=descending, True=ascending
  - `count` (int, default 10): Number of messages to retrieve
- **Returns**:
  - Failure: Dictionary containing `code` and `error`
  - Success: Dictionary containing `code` and message array

**Note**:
- The IM engine will automatically initialize and connect on the first call to any message-related tool
- Resource cleanup is automatically handled when the server disconnects

## Common Issues

### Q: Why does the server list show a yellow dot in Cursor even after configuration?

A: If the server list shows a yellow dot, try installing the UV command first, then restart Cursor and re-enable the service switch.

### Q: Why does Cherry Studio keep reporting errors?

A: Make sure both UV and Bun are installed successfully, restart Cherry Studio, and then re-enable the service switch.

### Q: Why do tool calls return errors?

A: Make sure environment variables (APP_KEY, TOKEN, NAVI_URL, AREA_CODE, STAT_URL) are correctly set, restart the service, and try calling the tools again.

## Technical Support

If you encounter issues, please:

1. Check if environment variables are correctly set
2. Check log output for specific error messages
3. Create an issue in the open source project
