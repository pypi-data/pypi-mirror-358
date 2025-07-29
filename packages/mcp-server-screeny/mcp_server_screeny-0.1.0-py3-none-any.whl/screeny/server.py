import subprocess
import tempfile
import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from base64 import b64encode
from typing import Dict, List, Any, Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS, INTERNAL_ERROR
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".screeny"
CONFIG_FILE = CONFIG_DIR / "approved_windows.json"

_approved_windows: Dict[str, Dict[str, Any]] = {}

mcp = FastMCP("Screeny")


class WindowInfo(BaseModel):
    """Information about a macOS window."""

    id: Annotated[str, Field(description="Unique window ID")]
    app: Annotated[str, Field(
        description="Application name that owns the window")]
    title: Annotated[str, Field(description="Window title")]
    approved: Annotated[bool, Field(
        default=False, description="Whether this window is approved for screenshots")]


class ScreenshotRequest(BaseModel):
    """Parameters for taking a screenshot of a window."""

    window_id: Annotated[str, Field(
        description="The window ID from listWindows to capture")]


class WindowSetupRequest(BaseModel):
    """Parameters for window setup operations."""

    approve_all: Annotated[bool, Field(
        default=False, description="Approve all windows without prompting")]


def ensure_config_dir():
    """Ensure the config directory exists"""
    CONFIG_DIR.mkdir(exist_ok=True)


def load_approved_windows() -> Dict[str, Dict[str, Any]]:
    """Load approved windows from persistent storage"""
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get('approved_windows', {})
    except Exception as e:
        logger.warning(f"Failed to load config: {e}")
        return {}


def save_approved_windows(windows: Dict[str, Dict[str, Any]]):
    """Save approved windows to persistent storage"""
    ensure_config_dir()
    try:
        config = {
            'approved_windows': windows,
            'last_updated': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")


def _is_user_application_window(window: Dict[str, Any]) -> bool:
    """
    Check if a window represents a user application window worth capturing.
    """
    owner_name = window.get("kCGWindowOwnerName", "")
    window_name = window.get("kCGWindowName", "")
    window_number = window.get("kCGWindowNumber")
    window_layer = window.get("kCGWindowLayer", 0)

    return (
        owner_name and
        window_name and
        window_number and
        window_layer <= 2 and
        len(window_name.strip()) > 0 and
        window_name != "Desktop" and
        not owner_name.startswith("com.apple.") and
        owner_name not in ["WindowServer", "Dock", "Wallpaper",
                           "SystemUIServer", "Control Center"]
    )


def get_all_windows() -> List[WindowInfo]:
    """
    Get all available windows using macOS Quartz framework.
    Returns real window IDs that work with screencapture -l.
    """
    try:
        from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionAll, kCGNullWindowID
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionAll, kCGNullWindowID)

        windows = []
        for window in window_list:
            if _is_user_application_window(window):
                windows.append(
                    WindowInfo(
                        id=str(window.get("kCGWindowNumber")),
                        app=window.get("kCGWindowOwnerName", ""),
                        title=window.get("kCGWindowName", ""),
                        approved=False
                    )
                )

        return windows

    except ImportError as e:
        logger.error("❌ Quartz framework not available!")
        logger.error(
            "   pyobjc-framework-Quartz is required but failed to import.")
        logger.error("   Try: pip install pyobjc-framework-Quartz")
        raise RuntimeError(
            "Quartz framework required but not available") from e
    except Exception as e:
        logger.error(f"❌ Failed to enumerate windows: {e}")
        raise RuntimeError(f"Window enumeration failed: {e}") from e


def setup_windows_interactive() -> Dict[str, Dict[str, Any]]:
    """Interactive terminal-based window approval with user prompts"""
    print("\n🪟 Screeny Window Approval Setup")
    print("=" * 40)

    try:
        current_windows = get_all_windows()
    except RuntimeError as e:
        print(f"❌ Cannot enumerate windows: {e}")
        return {}

    if not current_windows:
        print("❌ No windows found. Make sure you have applications open.")
        return {}

    print(f"Found {len(current_windows)} open windows:")
    print()

    approved = {}
    for i, window in enumerate(current_windows, 1):
        print(f"{i:2d}. {window.app} - {window.title}")

        while True:
            choice = input(
                f"    Approve this window? [y/n/q(uit)/a(ll)]: ").lower().strip()
            if choice in ['y', 'yes']:
                window_dict = window.model_dump()
                window_dict['approved'] = True
                approved[window.id] = window_dict
                print("    ✅ Approved")
                break
            elif choice in ['n', 'no']:
                print("    ❌ Skipped")
                break
            elif choice in ['a', 'all']:
                print("    ✅ Approving all remaining windows...")
                for remaining_window in current_windows[i-1:]:
                    window_dict = remaining_window.model_dump()
                    window_dict['approved'] = True
                    approved[remaining_window.id] = window_dict
                print(f"    ✅ Approved {len(current_windows) - i + 1} windows")
                return approved
            elif choice in ['q', 'quit']:
                print("\n🛑 Setup cancelled")
                return approved
            else:
                print("    Please enter y (yes), n (no), a (approve all), or q (quit)")

    print(f"\n✅ Setup complete! Approved {len(approved)} windows.")
    return approved


def setup_windows_approve_all() -> Dict[str, Dict[str, Any]]:
    """Auto-approve all current windows without prompting"""
    try:
        current_windows = get_all_windows()
    except RuntimeError as e:
        print(f"❌ Cannot enumerate windows: {e}")
        return {}

    if not current_windows:
        print("❌ No windows found. Make sure you have applications open.")
        return {}

    approved = {}
    for window in current_windows:
        window_dict = window.model_dump()
        window_dict['approved'] = True
        approved[window.id] = window_dict

    print(f"✅ Auto-approved all {len(approved)} windows.")
    return approved


def take_screenshot_direct(window_id: str, tmp_path: str) -> subprocess.CompletedProcess:
    """
    Take screenshot using direct window capture (requires Screen Recording permission).
    """
    logger.info(f"Taking screenshot of window {window_id}")
    result = subprocess.run(
        ['screencapture', '-x', '-l', window_id, tmp_path],
        capture_output=True, text=True, timeout=10
    )
    return result


def setup_mode(allow_all: bool = False):
    """Interactive setup mode for window approval"""
    print("🚀 Screeny Setup Mode")
    print("This will help you approve windows for screenshot capture.")
    print()

    if allow_all:
        print("🔓 Auto-approving all windows...")
        approved = setup_windows_approve_all()
    else:
        print("🔒 Interactive approval mode...")
        print("💡 Tip: Use 'a' to approve all remaining windows at any point")
        print()
        approved = setup_windows_interactive()

    if approved:
        save_approved_windows(approved)
        print(f"\n💾 Configuration saved to: {CONFIG_FILE}")
        print("\n📋 Summary:")
        for window in approved.values():
            print(f"   - {window['app']}: {window['title']}")
        print("\n💡 Grant Screen Recording permission when prompted!")
    else:
        print("\n❌ No windows approved. Run setup again when ready.")
        print("💡 Tip: Use --allow-all flag to approve all windows automatically:")
        print("   uv run python -m screeny --setup --allow-all")


def debug_mode():
    """Debug mode to test window enumeration and permissions"""
    print("🔍 Screeny Debug Mode")
    print("=" * 30)

    print("\n1. Testing Quartz framework...")
    try:
        windows = get_all_windows()
        print(f"✅ Quartz: Found {len(windows)} windows with real IDs")

        print("\n2. Current windows:")
        for w in windows[:10]:
            print(f"   - [{w.id}] {w.app}: {w.title}")
        if len(windows) > 10:
            print(f"   ... and {len(windows) - 10} more")

    except RuntimeError as e:
        print(f"❌ Quartz: {e}")
        return

    print("\n3. Recommendations:")
    print("   ✅ Quartz working optimally!")
    print("   💡 Grant Screen Recording permission when taking screenshots for best UX")


@mcp.tool(
    annotations={
        "title": "List Approved Windows",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def list_windows() -> list[TextContent]:
    """
    List all currently approved windows available for screenshot capture.

    Returns JSON with approved windows. If no windows are approved,
    returns an error instructing the user to run setup.
    """
    global _approved_windows

    if not _approved_windows:
        _approved_windows = load_approved_windows()

    try:
        current_windows = get_all_windows()
    except RuntimeError as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f'Failed to enumerate windows: {str(e)}. Ensure pyobjc-framework-Quartz is installed: pip install pyobjc-framework-Quartz'
        ))

    if not _approved_windows:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message='No approved windows found. Please run setup first: "uv run python -m screeny --setup" for interactive approval, or "uv run python -m screeny --setup --allow-all" to approve all windows automatically. Setup is required to approve which windows Screeny can capture screenshots of.'
        ))

    current_window_ids = {w.id for w in current_windows}

    still_open_approved = {}
    for window_id, window_info in _approved_windows.items():
        if window_info.get('approved') and window_id in current_window_ids:
            still_open_approved[window_id] = window_info

    if len(still_open_approved) != len(_approved_windows):
        _approved_windows = still_open_approved
        save_approved_windows(_approved_windows)
        logger.info(
            f"Removed {len(_approved_windows) - len(still_open_approved)} closed windows")

    result_data = {
        'approved_windows': list(_approved_windows.values()),
        'total_approved': len(_approved_windows),
        'config_file': str(CONFIG_FILE),
        'message': 'Use takeScreenshot with a window ID to capture. Run --setup to reconfigure.'
    }

    return [TextContent(
        type="text",
        text=json.dumps(result_data, indent=2)
    )]


@mcp.tool(
    annotations={
        "title": "Take Window Screenshot",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
def take_screenshot(request: ScreenshotRequest) -> list[ImageContent | TextContent]:
    """
    Take a screenshot of a specific window by its ID using direct capture.
    Requires Screen Recording permission.
    Run the setup command first to approve which windows can be captured.
    """
    global _approved_windows
    window_id = request.window_id

    if not window_id or not isinstance(window_id, str):
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="window_id must be a non-empty string"
        ))

    if not _approved_windows:
        _approved_windows = load_approved_windows()

    if window_id not in _approved_windows:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message=f"Window ID '{window_id}' not found in approved windows. Run listWindows first to see available windows, or run setup to approve new windows."
        ))

    window_info = _approved_windows[window_id]

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        result = take_screenshot_direct(window_id, tmp_path)

        if result.returncode != 0:
            if "not permitted" in result.stderr.lower() or "not authorized" in result.stderr.lower():
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Screen Recording permission required to capture '{window_info['title']}'. Grant Screen Recording permissions in System Settings > Privacy & Security > Screen Recording"
                ))
            else:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Screenshot failed for window '{window_info['title']}': {result.stderr}"
                ))

        tmp_file_path = Path(tmp_path)
        if not tmp_file_path.exists() or tmp_file_path.stat().st_size == 0:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Screenshot file was not created or is empty for window '{window_info['title']}'"
            ))

        image_data = tmp_file_path.read_bytes()
        base64_data = b64encode(image_data).decode('utf-8')

        logger.info(
            f"Successfully captured screenshot for window: {window_info['title']} ({len(image_data)} bytes)")

        metadata = {
            "window_id": window_id,
            "app": window_info['app'],
            "title": window_info['title'],
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        return [
            ImageContent(
                type="image",
                data=base64_data,
                mimeType="image/png"
            ),
            TextContent(
                type="text",
                text=f"Screenshot captured: {window_info['app']} - {window_info['title']}\n\nMetadata:\n{json.dumps(metadata, indent=2)}"
            )
        ]

    except subprocess.TimeoutExpired:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Screenshot timed out for window '{window_info['title']}'"
        ))
    except Exception as e:
        logger.error(f"Unexpected error taking screenshot: {e}")
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Unexpected error taking screenshot: {str(e)}"
        ))
    finally:
        try:
            if Path(tmp_path).exists():
                os.unlink(tmp_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {tmp_path}: {e}")


@mcp.resource("screeny://info")
def get_server_info() -> str:
    """Get information about the Screeny MCP server"""
    return json.dumps({
        "name": "Screeny MCP Server",
        "version": "0.1.0",
        "description": "Capture screenshots of specific application windows, providing visual context for development and debugging tasks",
        "capabilities": [
            "List application windows on macOS",
            "Capture screenshots of specific application windows",
            "Return screenshots as Base64-encoded PNG images",
            "Provide window metadata for analysis"
        ],
        "requirements": [
            "macOS only",
            "pyobjc-framework-Quartz",
            "Screen Recording permission"
        ],
        "tools": ["listWindows", "takeScreenshot"],
        "resources": ["screeny://info"],
        "config_file": str(CONFIG_FILE)
    }, indent=2)


def serve() -> None:
    """Run the Screeny MCP server."""
    logger.info("Starting Screeny MCP Server...")
    mcp.run()
