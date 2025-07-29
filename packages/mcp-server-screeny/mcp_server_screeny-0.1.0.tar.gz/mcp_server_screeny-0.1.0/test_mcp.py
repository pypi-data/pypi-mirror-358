#!/usr/bin/env python3
"""
Test script for Screeny MCP server functionality
"""

import asyncio
import json


async def test_mcp_server():
    """Test the MCP server tools"""
    print("🧪 Testing Screeny MCP Server")
    print("=" * 35)

    # Test 1: List windows
    print("\n1. Testing listWindows tool...")
    try:
        # Simulate calling the listWindows tool
        from screeny.server import list_windows
        result = list_windows()
        # Handle MCP TextContent format
        if isinstance(result, list) and len(result) > 0 and hasattr(result[0], 'text'):
            json_text = result[0].text
            data = json.loads(json_text)
        else:
            data = {"error": "Unexpected result format"}

        # Check if this is a setup error
        if 'error' in data and data['error'].get('code') == -10:
            print("⚠️  Setup required:")
            print(f"   Message: {data['error']['message']}")
            print("   Run setup with:")
            print(
                f"   - Interactive: {data['error']['setup_instructions']['interactive_setup']}")
            print(
                f"   - Auto-approve: {data['error']['setup_instructions']['approve_all']}")
        elif 'approved_windows' in data:
            print(f"✅ Found {data['total_approved']} approved windows")
            if data['approved_windows']:
                print("   Windows:")
                for window in data['approved_windows'][:3]:
                    print(f"   - {window['app']}: {window['title'][:50]}...")
            else:
                print("   No approved windows")
        else:
            print(f"❌ Unexpected response format: {data}")

    except Exception as e:
        print(f"❌ listWindows failed: {e}")

    # Test 2: Server info
    print("\n2. Testing server info resource...")
    try:
        from screeny.server import get_server_info
        info = get_server_info()
        data = json.loads(info)
        print(f"✅ Server: {data['name']} v{data['version']}")
        print(f"   Tools: {', '.join(data['tools'])}")
        print(f"   Config: {data['config_file']}")

    except Exception as e:
        print(f"❌ Server info failed: {e}")

    # Test 3: Screenshot (if we have approved windows)
    print("\n3. Testing takeScreenshot tool...")
    try:
        from screeny.server import list_windows, take_screenshot, ScreenshotRequest
        windows_result = list_windows()
        # Handle MCP TextContent format
        if isinstance(windows_result, list) and len(windows_result) > 0 and hasattr(windows_result[0], 'text'):
            json_text = windows_result[0].text
            windows_data = json.loads(json_text)
        else:
            windows_data = {"error": "Unexpected result format"}

        # Check if setup is required
        if 'error' in windows_data and windows_data['error'].get('code') == -10:
            print("   ⚠️  Cannot test screenshot - setup required first")
            print("   Run: uv run python -m screeny --setup")
        elif 'approved_windows' in windows_data and windows_data['approved_windows']:
            # Try to screenshot the first approved window
            first_window = windows_data['approved_windows'][0]
            window_id = first_window['id']

            print(
                f"   Attempting screenshot of: {first_window['app']} - {first_window['title'][:30]}...")
            screenshot_result = take_screenshot(
                ScreenshotRequest(window_id=window_id))

            # Handle MCP response with both ImageContent and TextContent
            if isinstance(screenshot_result, list) and len(screenshot_result) >= 1:
                image_content = None
                text_content = None

                for content in screenshot_result:
                    if hasattr(content, 'data') and content.type == "image":
                        image_content = content
                    elif hasattr(content, 'text') and content.type == "text":
                        text_content = content

                if image_content:
                    print(
                        f"✅ Screenshot captured: {len(image_content.data)} chars of Base64 data")
                    if text_content:
                        # First line only
                        print(
                            f"   Context: {text_content.text.split(chr(10))[0]}")
                else:
                    print(f"❌ No image content in response")
            else:
                print(f"❌ Unexpected screenshot response: {screenshot_result}")
        else:
            print("   ⚠️  No approved windows to screenshot")

    except Exception as e:
        print(f"❌ takeScreenshot failed: {e}")

    print("\n🎯 MCP Server Test Complete!")
    print("\nTo use with Claude Desktop:")
    print("1. Run: uv run python -m screeny --setup")
    print("2. Add to claude_desktop_config.json:")
    print(
        '   "screeny": {"command": "uv", "args": ["run", "python", "-m", "screeny"]}')

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
