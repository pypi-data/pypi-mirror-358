#!/usr/bin/env python3
"""Debug script to check version and compression behavior."""


def check_version():
    """Check what version is actually being used."""
    print("🔍 Version Check")
    print("=" * 30)

    try:
        import screeny
        print(f"Screeny version: {screeny.__version__}")
    except Exception as e:
        print(f"Error importing screeny: {e}")

    try:
        from screeny.server import get_server_info
        import json
        info = get_server_info()
        data = json.loads(info)
        print(f"Server reports version: {data['version']}")
    except Exception as e:
        print(f"Error getting server info: {e}")


def test_compression_directly():
    """Test compression function directly."""
    print("\n🧪 Direct Compression Test")
    print("=" * 30)

    try:
        import tempfile
        from pathlib import Path
        from PIL import Image
        from screeny.server import compress_image

        # Create test image
        img = Image.new('RGB', (1000, 1000), "red")
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            img.save(tmp_file.name, 'PNG')
            img_path = tmp_file.name

        original_size = Path(img_path).stat().st_size
        target_size = 100_000  # 100KB target

        print(f"Original: {original_size} bytes")
        print(f"Target: {target_size} bytes")

        compressed_data = compress_image(img_path, target_size)

        print(f"Result: {len(compressed_data)} bytes")
        print(f"Compression worked: {len(compressed_data) < original_size}")
        print(f"Under target: {len(compressed_data) <= target_size * 1.5}")

        Path(img_path).unlink()

    except Exception as e:
        print(f"Error in compression test: {e}")
        import traceback
        traceback.print_exc()


def check_mcp_behavior():
    """Check what the MCP functions actually return."""
    print("\n🔧 MCP Function Test")
    print("=" * 30)

    try:
        from screeny.server import list_windows
        import json

        # Test list_windows first
        result = list_windows()
        if result and hasattr(result[0], 'text'):
            data = json.loads(result[0].text)
            print(f"Windows found: {data.get('total_approved', 0)}")

            if data.get('approved_windows'):
                # Try a screenshot
                from screeny.server import take_screenshot, ScreenshotRequest

                window_id = data['approved_windows'][0]['id']
                window_title = data['approved_windows'][0]['title']

                print(f"Testing screenshot of: {window_title[:30]}...")

                # Test without compression
                print("\n  Without compression:")
                result_no_compress = take_screenshot(
                    ScreenshotRequest(window_id=window_id, compress=False))
                for content in result_no_compress:
                    if hasattr(content, 'data'):
                        print(
                            f"  Image data length: {len(content.data)} chars")
                        # Rough size estimate (base64 is ~4/3 of original)
                        estimated_bytes = len(content.data) * 3 // 4
                        print(
                            f"  Estimated raw size: {estimated_bytes} bytes ({estimated_bytes/1024:.1f} KB)")

                # Test with compression
                print("\n  With compression:")
                result_compress = take_screenshot(
                    ScreenshotRequest(window_id=window_id, compress=True))
                for content in result_compress:
                    if hasattr(content, 'data'):
                        print(
                            f"  Image data length: {len(content.data)} chars")
                        estimated_bytes = len(content.data) * 3 // 4
                        print(
                            f"  Estimated raw size: {estimated_bytes} bytes ({estimated_bytes/1024:.1f} KB)")

                        # Check if they're the same
                        no_compress_data = None
                        for c in result_no_compress:
                            if hasattr(c, 'data'):
                                no_compress_data = c.data
                                break

                        if no_compress_data and content.data == no_compress_data:
                            print(
                                "  ⚠️  WARNING: Compressed and uncompressed data are identical!")
                        else:
                            print(
                                "  ✅ Compressed and uncompressed data are different")
            else:
                print("No approved windows to test with")
        else:
            print("Failed to get windows list")

    except Exception as e:
        print(f"Error in MCP test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_version()
    test_compression_directly()
    check_mcp_behavior()

    print(f"\n💡 If you're getting exactly 1048576 bytes, that's suspiciously exactly 1MB.")
    print(f"   This might indicate the MCP host is truncating responses at 1MB.")
    print(f"   Try with compress=true to see if that helps.")
