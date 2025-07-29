# Screeny MCP Server

A **macOS-only MCP server** that enables LLMs to capture and analyze screenshots of specific application windows, providing visual context for development and debugging tasks.

> [!IMPORTANT]
> Requires **Screen Recording permission** - you'll be prompted when first taking screenshots.

### Available Tools

- `listWindows` - Lists all approved application windows available for screenshot capture.

  - Only shows user approved windows

- `takeScreenshot` - Captures a screenshot of a specific window by its ID.
  - **Captures windows in background** - no need to bring to front, works with minimized windows
  - **Provides actual pixel data** - full-fidelity image, not OCR or text extraction

### Resources

- `screeny://info` - Server information and configuration details

## Setup

### 1. Window Approval (Required)

Approve which windows can be captured:

```bash
# Navigate to screeny directory
cd /path/to/screeny

# With uv (recommended)
uv run python -m screeny --setup

# Or with regular Python (requires manual dependency install)
pip install -e .
python -m screeny --setup

# Optionally, auto-approve all current windows in one go
uv run python -m screeny --setup --allow-all
```

Approvals are saved to `~/.screeny/approved_windows.json`. Re-run setup when you want to update the list of approved windows.

### 2. Grant Screen Recording Permission

Go to **System Settings** > **Privacy & Security** > **Screen Recording** and enable permission for the host. You may need to restart the application after granting permission.

## Configuration

### Claude Desktop

1. Open Claude settings → Developer → Edit Config
2. Add configuration:

**Recommended (using uvx):**

```json
{
  "mcpServers": {
    "screeny": {
      "command": "uvx",
      "args": ["--from", "/path/to/screeny", "mcp-server-screeny"]
    }
  }
}
```

**Once published to PyPI (coming soon):**

```json
{
  "mcpServers": {
    "screeny": {
      "command": "uvx",
      "args": ["mcp-server-screeny"]
    }
  }
}
```

**Alternative (using uv):**

```json
{
  "mcpServers": {
    "screeny": {
      "command": "uv",
      "args": ["run", "python", "-m", "screeny"],
      "cwd": "/path/to/screeny",
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

<details>
<summary>Using pip instead of uv</summary>

```json
{
  "mcpServers": {
    "screeny": {
      "command": "python",
      "args": ["-m", "screeny"],
      "cwd": "/path/to/screeny"
    }
  }
}
```

**Note:** First run `pip install -e .` in the screeny directory to install dependencies from `pyproject.toml`.

</details>

### Cursor

1. Open Cursor settings → Tools & Integrations → MCP Tools
2. Add configuration:

**Recommended (using uvx):**

```json
{
  "screeny": {
    "command": "uvx",
    "args": ["--from", "/path/to/screeny", "mcp-server-screeny"]
  }
}
```

**Once published to PyPI (coming soon):**

```json
{
  "screeny": {
    "command": "uvx",
    "args": ["mcp-server-screeny"]
  }
}
```

**Alternative (using uv):**

```json
{
  "screeny": {
    "command": "uv",
    "args": ["run", "python", "-m", "screeny"],
    "cwd": "/path/to/screeny",
    "env": {
      "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
    }
  }
}
```

<details>
<summary>Using pip instead of uv</summary>

```json
{
  "screeny": {
    "command": "python",
    "args": ["-m", "screeny"],
    "cwd": "/path/to/screeny"
  }
}
```

**Note:** First run `pip install -e .` in the screeny directory to install dependencies from `pyproject.toml`.

</details>

## Usage

1. Run setup (one time): `uv run python -m screeny --setup`
2. Configure MCP client with above settings
3. Ask your LLM to list windows and take screenshots

## Security & Privacy

- **Explicit consent**: Only user-approved windows can be captured
- **Local processing**: All data stays on your machine, no external transmission
- **Temporary storage**: Screenshots are saved to a temporary file, encoded as base64, and deleted immediately after. No screenshot data remains on disk after use.

## Troubleshooting

### Permission Issues

```bash
# Test window detection and permissions
uv run python -m screeny --debug

# Re-run setup if windows changed
uv run python -m screeny --setup
```

### Common Issues

**"Quartz framework not available"**

- Solution: Install dependencies with `pip install -e .` or ensure internet connection for automatic installation

**"No approved windows found"**

- Solution: Run `uv run python -m screeny --setup` first

**"Screen Recording permission required"**

- Solution: Grant permission in System Settings > Privacy & Security > Screen Recording

## Contributing

Pull requests are welcome! Feel free to contribute new ideas, bug fixes, or enhancements.

## Requirements

- Python 3.10+
- macOS (uses Quartz framework)

## License

MIT License
