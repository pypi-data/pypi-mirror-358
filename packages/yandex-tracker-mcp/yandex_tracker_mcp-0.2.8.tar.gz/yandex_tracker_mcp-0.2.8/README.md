# Yandex Tracker MCP Server

![PyPI - Version](https://img.shields.io/pypi/v/yandex-tracker-mcp)

A comprehensive Model Context Protocol (MCP) server that enables AI assistants to interact with Yandex Tracker APIs. This server provides secure, authenticated access to Yandex Tracker issues, queues, comments, worklogs, and search functionality with optional Redis caching for improved performance.

## Features

- **Complete Queue Management**: List and access all available Yandex Tracker queues with pagination support and tag retrieval
- **User Management**: Retrieve user account information, including login details, email addresses, license status, and organizational data
- **Issue Operations**: Retrieve detailed issue information, comments, related links, worklogs, and attachments
- **Field Management**: Access global fields, queue-specific local fields, statuses, and issue types
- **Advanced Query Language**: Full Yandex Tracker Query Language support with complex filtering, sorting, and date functions
- **Performance Caching**: Optional Redis caching layer for improved response times
- **Security Controls**: Configurable queue access restrictions and secure token handling
- **Multiple Transport Options**: Support for stdio and SSE transports
- **Organization Support**: Compatible with both standard and cloud organization IDs

## Prerequisites

- Python 3.12 or higher
- Valid Yandex Tracker API token with appropriate permissions
- Optional: Redis server for caching functionality

### Organization ID Configuration

Choose one of the following based on your Yandex organization type:

- **Yandex Cloud Organization**: Use `TRACKER_CLOUD_ORG_ID` env var later for Yandex Cloud-managed organizations
- **Yandex 360 Organization**: Use `TRACKER_ORG_ID` env var later for Yandex 360 organizations

You can find your organization ID in the Yandex Tracker URL or organization settings.


## MCP Client Configuration

The following sections show how to configure the MCP server for different AI clients. You can use either `uvx yandex-tracker-mcp@latest` or the Docker image `ghcr.io/aikts/yandex-tracker-mcp:latest`. Both require these environment variables:

- `TRACKER_TOKEN` - Your Yandex Tracker OAuth token (required)
- `TRACKER_CLOUD_ORG_ID` - Your Yandex Cloud organization ID
- `TRACKER_ORG_ID` - Your Yandex 360 organization ID

<details>
<summary><strong>Claude Desktop</strong></summary>

**Configuration file path:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Using uvx:**
```json
{
  "mcpServers": {
    "yandex-tracker": {
      "command": "uvx",
      "args": ["yandex-tracker-mcp@latest"],
      "env": {
        "TRACKER_TOKEN": "your_tracker_token_here",
        "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
        "TRACKER_ORG_ID": "your_org_id_here"
      }
    }
  }
}
```

**Using Docker:**
```json
{
  "mcpServers": {
    "yandex-tracker": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "TRACKER_TOKEN",
        "-e", "TRACKER_CLOUD_ORG_ID",
        "-e", "TRACKER_ORG_ID",
        "ghcr.io/aikts/yandex-tracker-mcp:latest"
      ],
      "env": {
        "TRACKER_TOKEN": "your_tracker_token_here",
        "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
        "TRACKER_ORG_ID": "your_org_id_here"
      }
    }
  }
}
```

</details>

<details>
<summary><strong>Claude Code</strong></summary>

**Using uvx:**
```bash
claude mcp add yandex-tracker uvx yandex-tracker-mcp@latest \
  -e TRACKER_TOKEN=your_tracker_token_here \
  -e TRACKER_CLOUD_ORG_ID=your_cloud_org_id_here \
  -e TRACKER_ORG_ID=your_org_id_here \
  -e TRANSPORT=stdio
```

**Using Docker:**
```bash
claude mcp add yandex-tracker docker "run --rm -i -e TRACKER_TOKEN=your_tracker_token_here -e TRACKER_CLOUD_ORG_ID=your_cloud_org_id_here -e TRACKER_ORG_ID=your_org_id_here -e TRANSPORT=stdio ghcr.io/aikts/yandex-tracker-mcp:latest"
```

</details>

<details>
<summary><strong>Cursor</strong></summary>

**Configuration file path:**
- Project-specific: `.cursor/mcp.json` in your project directory
- Global: `~/.cursor/mcp.json`

**Using uvx:**
```json
{
  "mcpServers": {
    "yandex-tracker": {
      "command": "uvx",
      "args": ["yandex-tracker-mcp@latest"],
      "env": {
        "TRACKER_TOKEN": "your_tracker_token_here",
        "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
        "TRACKER_ORG_ID": "your_org_id_here"
      }
    }
  }
}
```

**Using Docker:**
```json
{
  "mcpServers": {
    "yandex-tracker": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "TRACKER_TOKEN",
        "-e", "TRACKER_CLOUD_ORG_ID",
        "-e", "TRACKER_ORG_ID",
        "ghcr.io/aikts/yandex-tracker-mcp:latest"
      ],
      "env": {
        "TRACKER_TOKEN": "your_tracker_token_here",
        "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
        "TRACKER_ORG_ID": "your_org_id_here"
      }
    }
  }
}
```

</details>

<details>
<summary><strong>Windsurf</strong></summary>

**Configuration file path:**
- `~/.codeium/windsurf/mcp_config.json`

Access via: Windsurf Settings → Cascade tab → Model Context Protocol (MCP) Servers → "View raw config"

**Using uvx:**
```json
{
  "mcpServers": {
    "yandex-tracker": {
      "command": "uvx",
      "args": ["yandex-tracker-mcp@latest"],
      "env": {
        "TRACKER_TOKEN": "your_tracker_token_here",
        "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
        "TRACKER_ORG_ID": "your_org_id_here"
      }
    }
  }
}
```

**Using Docker:**
```json
{
  "mcpServers": {
    "yandex-tracker": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "TRACKER_TOKEN",
        "-e", "TRACKER_CLOUD_ORG_ID",
        "-e", "TRACKER_ORG_ID",
        "ghcr.io/aikts/yandex-tracker-mcp:latest"
      ],
      "env": {
        "TRACKER_TOKEN": "your_tracker_token_here",
        "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
        "TRACKER_ORG_ID": "your_org_id_here"
      }
    }
  }
}
```

</details>

<details>
<summary><strong>Zed</strong></summary>

**Configuration file path:**
- `~/.config/zed/settings.json`

Access via: `Cmd+,` (macOS) or `Ctrl+,` (Linux/Windows) or command palette: "zed: open settings"

**Note:** Requires Zed Preview version for MCP support.

**Using uvx:**
```json
{
  "context_servers": {
    "yandex-tracker": {
      "source": "custom",
      "command": {
        "path": "uvx",
        "args": ["yandex-tracker-mcp@latest"],
        "env": {
          "TRACKER_TOKEN": "your_tracker_token_here",
          "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
          "TRACKER_ORG_ID": "your_org_id_here"
        }
      }
    }
  }
}
```

**Using Docker:**
```json
{
  "context_servers": {
    "yandex-tracker": {
      "source": "custom",
      "command": {
        "path": "docker",
        "args": [
          "run", "--rm", "-i",
          "-e", "TRACKER_TOKEN",
          "-e", "TRACKER_CLOUD_ORG_ID",
          "-e", "TRACKER_ORG_ID",
          "ghcr.io/aikts/yandex-tracker-mcp:latest"
        ],
        "env": {
          "TRACKER_TOKEN": "your_tracker_token_here",
          "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
          "TRACKER_ORG_ID": "your_org_id_here"
        }
      }
    }
  }
}
```

</details>

<details>
<summary><strong>GitHub Copilot (VS Code)</strong></summary>

**Configuration file path:**
- Workspace: `.vscode/mcp.json` in your project directory
- Global: VS Code `settings.json`

**Option 1: Workspace Configuration (Recommended for security)**

Create `.vscode/mcp.json`:

**Using uvx:**
```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "tracker-token",
      "description": "Yandex Tracker Token",
      "password": true
    },
    {
      "type": "promptString",
      "id": "cloud-org-id",
      "description": "Yandex Cloud Organization ID"
    },
    {
      "type": "promptString",
      "id": "org-id",
      "description": "Yandex Tracker Organization ID (optional)"
    }
  ],
  "servers": {
    "yandex-tracker": {
      "type": "stdio",
      "command": "uvx",
      "args": ["yandex-tracker-mcp@latest"],
      "env": {
        "TRACKER_TOKEN": "${input:tracker-token}",
        "TRACKER_CLOUD_ORG_ID": "${input:cloud-org-id}",
        "TRACKER_ORG_ID": "${input:org-id}",
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

**Using Docker:**
```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "tracker-token",
      "description": "Yandex Tracker Token",
      "password": true
    },
    {
      "type": "promptString",
      "id": "cloud-org-id",
      "description": "Yandex Cloud Organization ID"
    },
    {
      "type": "promptString",
      "id": "org-id",
      "description": "Yandex Tracker Organization ID (optional)"
    }
  ],
  "servers": {
    "yandex-tracker": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "TRACKER_TOKEN",
        "-e", "TRACKER_CLOUD_ORG_ID",
        "-e", "TRACKER_ORG_ID",
        "ghcr.io/aikts/yandex-tracker-mcp:latest"
      ],
      "env": {
        "TRACKER_TOKEN": "${input:tracker-token}",
        "TRACKER_CLOUD_ORG_ID": "${input:cloud-org-id}",
        "TRACKER_ORG_ID": "${input:org-id}",
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

**Option 2: Global Configuration**

Add to VS Code `settings.json`:

**Using uvx:**
```json
{
  "github.copilot.chat.mcp.servers": {
    "yandex-tracker": {
      "type": "stdio",
      "command": "uvx",
      "args": ["yandex-tracker-mcp@latest"],
      "env": {
        "TRACKER_TOKEN": "your_tracker_token_here",
        "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
        "TRACKER_ORG_ID": "your_org_id_here"
      }
    }
  }
}
```

**Using Docker:**
```json
{
  "github.copilot.chat.mcp.servers": {
    "yandex-tracker": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "TRACKER_TOKEN",
        "-e", "TRACKER_CLOUD_ORG_ID",
        "-e", "TRACKER_ORG_ID",
        "ghcr.io/aikts/yandex-tracker-mcp:latest"
      ],
      "env": {
        "TRACKER_TOKEN": "your_tracker_token_here",
        "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
        "TRACKER_ORG_ID": "your_org_id_here"
      }
    }
  }
}
```

</details>

<details>
<summary><strong>Other MCP-Compatible Clients</strong></summary>

For other MCP-compatible clients, use the standard MCP server configuration format:

**Using uvx:**
```json
{
  "mcpServers": {
    "yandex-tracker": {
      "command": "uvx",
      "args": ["yandex-tracker-mcp@latest"],
      "env": {
        "TRACKER_TOKEN": "your_tracker_token_here",
        "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
        "TRACKER_ORG_ID": "your_org_id_here"
      }
    }
  }
}
```

**Using Docker:**
```json
{
  "mcpServers": {
    "yandex-tracker": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "TRACKER_TOKEN",
        "-e", "TRACKER_CLOUD_ORG_ID",
        "-e", "TRACKER_ORG_ID",
        "ghcr.io/aikts/yandex-tracker-mcp:latest"
      ],
      "env": {
        "TRACKER_TOKEN": "your_tracker_token_here",
        "TRACKER_CLOUD_ORG_ID": "your_cloud_org_id_here",
        "TRACKER_ORG_ID": "your_org_id_here"
      }
    }
  }
}
```

</details>

**Important Notes:**
- Replace placeholder values with your actual credentials
- Restart your AI client after configuration changes
- Ensure `uvx` is installed and available in your system PATH
- For production use, consider using environment variables instead of hardcoding tokens

## Available MCP Tools

The server exposes the following tools through the MCP protocol:

### Queue Management
- **`queues_get_all`**: List all available Yandex Tracker queues
  - Returns paginated queue information
  - Respects `TRACKER_LIMIT_QUEUES` restrictions

- **`queue_get_local_fields`**: Get local fields for a specific queue
  - Parameters: `queue_id` (string, queue key like "SOMEPROJECT")
  - Returns queue-specific custom fields with id, name, and key
  - Respects `TRACKER_LIMIT_QUEUES` restrictions

- **`queue_get_tags`**: Get all tags for a specific queue
  - Parameters: `queue_id` (string, queue key like "SOMEPROJECT")
  - Returns list of available tags in the specified queue
  - Respects `TRACKER_LIMIT_QUEUES` restrictions

### User Management
- **`users_get_all`**: Get information about user accounts registered in the organization
  - Parameters:
    - `per_page` (optional): Number of users per page (default: 50)
    - `page` (optional): Page number to return (default: 1)
  - Returns paginated list of users with login, email, license status, and organizational details
  - Includes user metadata such as external status, dismissal status, and notification preferences

- **`user_get`**: Get information about a specific user by login or UID
  - Parameters: `user_id` (string, user login like "john.doe" or UID like "12345")
  - Returns detailed user information including login, email, license status, and organizational details
  - Supports both user login names and numeric user IDs for flexible identification

### Field Management
- **`get_global_fields`**: Get all global fields available in Yandex Tracker
  - Returns complete list of global fields that can be used in issues
  - Includes field schema, type information, and configuration

### Status and Type Management
- **`get_statuses`**: Get all available issue statuses
  - Returns complete list of issue statuses that can be assigned
  - Includes status IDs, names, and type information

- **`get_issue_types`**: Get all available issue types
  - Returns complete list of issue types for creating/updating issues
  - Includes type IDs, names, and configuration details

### Issue Operations
- **`issue_get`**: Retrieve detailed issue information by ID
  - Parameters: `issue_id` (string, format: "QUEUE-123")
  - Returns complete issue data including status, assignee, description, etc.

- **`issue_get_url`**: Generate web URL for an issue
  - Parameters: `issue_id` (string)
  - Returns: `https://tracker.yandex.ru/{issue_id}`

- **`issue_get_comments`**: Fetch all comments for an issue
  - Parameters: `issue_id` (string)
  - Returns chronological list of comments with metadata

- **`issue_get_links`**: Get related issue links
  - Parameters: `issue_id` (string)
  - Returns links to related, blocked, or duplicate issues

- **`issue_get_worklogs`**: Retrieve worklog entries
  - Parameters: `issue_ids` (array of strings)
  - Returns time tracking data for specified issues

- **`issue_get_attachments`**: Get attachments for an issue
  - Parameters: `issue_id` (string, format: "QUEUE-123")
  - Returns list of attachments with metadata for the specified issue

### Search and Discovery
- **`issues_find`**: Search issues using [Yandex Tracker Query Language](https://yandex.ru/support/tracker/ru/user/query-filter)
  - Parameters:
    - `query` (required): Query string using Yandex Tracker Query Language syntax
    - `page` (optional): Page number for pagination (default: 1)
  - Returns up to 500 issues per page

## Configuration

### Environment Variables

```env
# Required - Yandex Tracker API token
TRACKER_TOKEN=your_yandex_tracker_oauth_token

# Organization Configuration (choose one)
TRACKER_CLOUD_ORG_ID=your_cloud_org_id    # For Yandex Cloud organizations
TRACKER_ORG_ID=your_org_id                # For Yandex 360 organizations

# Security - Restrict access to specific queues (optional)
TRACKER_LIMIT_QUEUES=PROJ1,PROJ2,DEV      # Comma-separated queue keys

# SSE Server Configuration
HOST=0.0.0.0                              # Default: 0.0.0.0
PORT=8001                                 # Default: 8001
TRANSPORT=stdio                           # Options: stdio, sse

# Redis Caching (optional but recommended for production)
CACHE_ENABLED=true                        # Default: false
CACHE_REDIS_ENDPOINT=localhost            # Default: localhost
CACHE_REDIS_PORT=6379                     # Default: 6379
CACHE_REDIS_DB=0                          # Default: 0
```

## Docker Deployment

### Using Pre-built Image (Recommended)

```bash
# Using environment file
docker run --env-file .env -p 8001:8001 ghcr.io/aikts/yandex-tracker-mcp:latest

# With inline environment variables
docker run -e TRACKER_TOKEN=your_token \
           -e TRACKER_CLOUD_ORG_ID=your_org_id \
           -e CACHE_ENABLED=true \
           -p 8001:8001 \
           ghcr.io/aikts/yandex-tracker-mcp:latest
```

### Building the Image Locally

```bash
docker build -t yandex-tracker-mcp .
```

### Docker Compose

**Using pre-built image:**
```yaml
version: '3.8'
services:
  mcp-tracker:
    image: ghcr.io/aikts/yandex-tracker-mcp:latest
    ports:
      - "8001:8001"
    environment:
      - TRACKER_TOKEN=${TRACKER_TOKEN}
      - TRACKER_CLOUD_ORG_ID=${TRACKER_CLOUD_ORG_ID}
```

**Building locally:**
```yaml
version: '3.8'
services:
  mcp-tracker:
    build: .
    ports:
      - "8001:8001"
    environment:
      - TRACKER_TOKEN=${TRACKER_TOKEN}
      - TRACKER_CLOUD_ORG_ID=${TRACKER_CLOUD_ORG_ID}
```

## Running in SSE Mode

The MCP server can also be run in Server-Sent Events (SSE) mode for web-based integrations or when stdio transport is not suitable.

### SSE Mode Environment Variables

```env
# Required - Set transport to SSE mode
TRANSPORT=sse

# Server Configuration
HOST=0.0.0.0                              # Default: 0.0.0.0 (all interfaces)
PORT=8001                                 # Default: 8001

# Required - Yandex Tracker API credentials
TRACKER_TOKEN=your_yandex_tracker_oauth_token
TRACKER_CLOUD_ORG_ID=your_cloud_org_id    # For Yandex Cloud organizations
TRACKER_ORG_ID=your_org_id                # For Yandex 360 organizations (optional)

# Optional - Other configurations
TRACKER_LIMIT_QUEUES=PROJ1,PROJ2,DEV      # Comma-separated queue keys
```

### Starting the SSE Server

```bash
# Basic SSE server startup
TRANSPORT=sse uvx yandex-tracker-mcp@latest

# With custom host and port
TRANSPORT=sse HOST=localhost PORT=9000 uvx yandex-tracker-mcp@latest

# With all environment variables
TRANSPORT=sse \
HOST=0.0.0.0 \
PORT=8001 \
TRACKER_TOKEN=your_token \
TRACKER_CLOUD_ORG_ID=your_org_id \
uvx yandex-tracker-mcp@latest
```

### Development Setup

```bash
# Clone and setup
git clone https://github.com/aikts/yandex-tracker-mcp
cd yandex-tracker-mcp

# Install development dependencies
uv sync --dev

# Formatting and static checking
make
```

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## Support

For issues and questions:
- Review Yandex Tracker API documentation
- Submit issues at https://github.com/aikts/yandex-tracker-mcp/issues
