# AI and Mobile Apps - Personal

Repository for AI-assisted mobile app development and Android device automation via MCP.

## Android MCP Server Setup

This project uses **DeepADB** - a comprehensive Model Context Protocol server for Android device automation with 209 tools across 49 modules.

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

3. **Install Node.js (if not already installed):**
   - Node.js: https://nodejs.org/ (install LTS version, add to PATH)

### DeepADB Installation

DeepADB is included as a submodule in this repository. To set it up:

```bash
cd DeepADB
npm ci
npm run build
```

### MCP Server Configuration

The MCP configuration is already set up in `.devin/mcp_config.json`:

```json
{
  "mcpServers": {
    "deepadb": {
      "command": "node",
      "args": ["C:\\Users\\DBTECH AFRICA\\Desktop\\AI with Mobile Apps\\DeepADB\\build\\index.js"],
      "env": {
        "ADB_PATH": "C:\\Platform-Tools\\adb.exe"
      }
    }
  }
}
```

### Available Features

DeepADB provides comprehensive Android automation capabilities:

**Device & Diagnostics:**
- Device info, health checks, runtime audit
- Battery, network, telephony, and performance profiling
- Bug reports, crash logs, and heap dumps

**UI Automation:**
- Screenshots (including annotated with UI elements)
- UI hierarchy dump and element search
- Tap, swipe, text input, and key events
- Screen recording

**App Management:**
- Install/uninstall APKs
- List packages and permissions
- Grant/revoke permissions
- Force-stop, start, and restart apps
- Intent resolution

**File Operations:**
- Push/pull files, list directories
- File creation, deletion, move, copy
- Search, grep, and checksum verification
- Permissions and ownership management

**Shell & Logs:**
- Execute shell commands (with security checks)
- Root shell access (requires rooted device)
- Logcat filtering and persistent watchers
- Database inspection (SQLite)

**Advanced Features:**
- Network capture and routing analysis
- Baseband and firmware analysis
- SELinux auditing
- Device profiles and workflows
- Wear OS support
- Multi-device orchestration

### Quick Test

After setup:
1. Connect your Android device via USB
2. Run: `adb devices` (should show your device)
3. Restart your IDE to load the MCP configuration
4. The DeepADB server will be available to AI assistants

## Usage Examples

```bash
# Check device health
# AI can invoke: adb_health_check

# List connected devices
# AI can invoke: adb_devices

# Take screenshot with UI annotations
# AI can invoke: adb_screencap_annotated

# Get screen state and UI elements
# AI can invoke: adb_screen_state

# Install an APK
# AI can invoke: adb_install path/to/app.apk

# Launch an app
# AI can invoke: adb_start_app com.example.app

# Tap on a UI element
# AI can invoke: adb_ui_find "Button text" then adb_input tap

# Get device diagnostics
# AI can invoke: adb_device_info, adb_battery, adb_network
```

## DeepADB Architecture

DeepADB operates in two modes:

1. **ADB Mode (default)**: Runs on your PC and communicates with the device over USB via ADB
2. **On-Device Mode**: Runs directly on the Android device (via Termux) with direct command execution

For more details, see the [DeepADB documentation](https://github.com/fullread/DeepADB).

## Airtel Money API Integration

This project includes a complete Airtel Money API integration for payment processing and airtime purchases.

### Components

1. **API Client** (`airtel_api_client.py`)
   - OAuth2 authentication with automatic token refresh
   - USSD push payment collection
   - Payment disbursement (B2C)
   - Transaction status enquiries
   - Refund processing

2. **Webhook Server** (`airtel_webhook_server.py`)
   - Flask server for transaction callbacks
   - Handles payment status updates
   - Transaction history tracking
   - Health check endpoints

3. **Airtime Purchase Module** (`airtel_airtime_purchase.py`)
   - Specialized airtime top-up implementation
   - REST API for airtime purchases
   - Transaction status monitoring
   - Complete purchase flow management

4. **Testing Suite** (`test_airtel_api.py`)
   - Automated testing for all components
   - Interactive testing mode
   - Comprehensive test coverage

### Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Credentials**
   ```bash
   cp .env.example .env
   # Edit .env with your Airtel Developer Portal credentials
   ```

3. **Run Tests**
   ```bash
   # Automated tests
   python test_airtel_api.py

   # Interactive testing
   python test_airtel_api.py --interactive
   ```

### Usage

```python
from airtel_api_client import AirtelMoneyClient

# Initialize client
client = AirtelMoneyClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    sandbox=True
)

# Authenticate
client.authenticate()

# USSD Push for payment
response = client.ussd_push(
    msisdn="712345678",
    amount=100.0,
    reference="Airtime Purchase",
    transaction_id="TXN_1234567890"
)

# Check status
status = client.collection_enquiry("TXN_1234567890")
```

### Documentation

See [AIRTEL_API_INTEGRATION.md](AIRTEL_API_INTEGRATION.md) for complete documentation including:
- API endpoint reference
- Security best practices
- Deployment guide
- Troubleshooting

**Official Documentation:**
- Airtel Developer Portal: https://developers.airtel.africa/docs
- API Documentation: https://developers.airtelkenya.com/documentation

## Security Notes

- USB debugging gives full device access
- Only connect trusted devices
- Disable USB debugging when not in use
- Review which operations you allow the AI to perform
- DeepADB includes security middleware and input sanitization
- **Airtel API**: Never commit credentials to version control; use environment variables

## Resources

- DeepADB: https://github.com/fullread/DeepADB
- ADB Documentation: https://developer.android.com/studio/command-line/adb
- Model Context Protocol: https://modelcontextprotocol.io/
- Airtel Developer Portal: https://developers.airtel.africa
