# AI and Mobile Apps - Personal

Repository for AI-assisted mobile app development and Android device automation via MCP.

## Android MCP Server Setup

This project uses **mcadb** - a Model Context Protocol server that gives AI assistants direct control over Android devices through ADB.

### Prerequisites

1. **Install ADB (Android Debug Bridge) on Windows:**
   - Download Android SDK Platform Tools from: https://developer.android.com/tools/releases/platform-tools
   - Extract to `C:\Platform-Tools`
   - Add to PATH:
     - Search for "Environment Variables" in Windows
     - Edit "Path" under User variables
     - Add `C:\Platform-Tools`
   - Verify: Open new terminal and run `adb version`

2. **Enable USB Debugging on Android Device:**
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times to enable Developer Options
   - Go to Settings → Developer Options
   - Enable "USB Debugging"
   - Connect device via USB and accept debugging prompt on phone

3. **Install Python and uv (if not already installed):**
   - Python: https://www.python.org/downloads/ (install for all users, add to PATH)
   - uv: `pip install uv` or visit https://github.com/astral-sh/uv

### MCP Server Configuration

Add this to your Devin/MCP client configuration (typically in `~/.config/devin/mcp_config.json` or similar):

```json
{
  "mcpServers": {
    "android": {
      "command": "uvx",
      "args": ["mcadb"],
      "env": {
        "ADB_PATH": "C:\\Platform-Tools\\adb.exe"
      }
    }
  }
}
```

### Available Features

Once configured, you can:
- **Device Control**: List devices, get device info, connect wirelessly
- **Screen Operations**: Take screenshots, tap, swipe, scroll
- **App Management**: Launch apps, get installed packages, clear app data
- **File Operations**: Push/pull files, list directories
- **Shell Commands**: Run commands on device (if enabled)
- **UI Inspection**: Dump UI hierarchy, find elements by text/ID

### Quick Test

After setup:
1. Connect your Android device via USB
2. Run: `adb devices` (should show your device)
3. The MCP server will be available to AI assistants

## Usage Examples

```bash
# List connected devices
# AI can invoke: devices_list

# Take a screenshot
# AI can invoke: screen_capture

# Launch an app
# AI can invoke: launch_app com.example.app

# Tap a screen coordinate
# AI can invoke: input_tap 500 1000
```

## Security Notes

- USB debugging gives full device access
- Only connect trusted devices
- Disable USB debugging when not in use
- Review which operations you allow the AI to perform

## Resources

- mcadb: https://pypi.org/project/mcadb/
- ADB Documentation: https://developer.android.com/studio/command-line/adb
