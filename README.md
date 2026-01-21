# Pi Home Server

SMS-controlled door opener for Raspberry Pi. Send a text to open your office door using Avigilon access control.

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Flip phone  │ ──── │   Twilio    │ ──── │   Pi        │ ──── │  Avigilon   │
│ sends SMS   │      │   webhook   │      │   server    │      │  web UI     │
│ "door"      │      │             │      │  (Playwright)│      │             │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
```

## Features

- **SMS Commands**: Control via text messages (no smartphone needed)
- **Secure**: Phone number allowlist + Twilio webhook validation
- **Persistent Session**: Cookies saved locally, no repeated logins
- **Rate Limited**: Max 10 requests per hour per phone number
- **Status Checks**: Query server and session health via SMS

## Prerequisites

- Raspberry Pi 5 (4GB) running Raspberry Pi OS Lite
- Twilio account (for SMS gateway)
- Avigilon access control account
- Way to expose Pi to internet (ngrok, Cloudflare Tunnel, or VPS)

## Quick Start (Testing on Mac/Linux)

```bash
# Clone repo
git clone https://github.com/jberusch/pi-home-server.git
cd pi-home-server

# Run setup script (installs dependencies)
chmod +x start.sh
./start.sh

# Authenticate with Avigilon (saves session)
source venv/bin/activate
python auth.py

# Test door opening
python door.py

# Start server and test locally
uvicorn main:app --reload
```

See "Raspberry Pi Setup" below for production deployment.

---

## Raspberry Pi Setup (Production)

Follow these steps to deploy on your Raspberry Pi 5 as an always-on server.

### Prerequisites

- Raspberry Pi 5 (4GB RAM recommended)
- Raspberry Pi OS Lite (64-bit) installed
- Pi connected to network (WiFi or Ethernet)
- Monitor and keyboard plugged into Pi for initial setup
- Twilio account configured (see TWILIO_SETUP.md)

### Step 1: Initial Pi Setup

Boot up your Pi with monitor/keyboard connected:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install git if not already installed
sudo apt install git -y

# Verify Python 3.9+ is installed
python3 --version
```

### Step 2: Clone Repository

```bash
cd ~
git clone https://github.com/jberusch/pi-home-server.git
cd pi-home-server
```

### Step 3: Create .env File

Create your environment configuration:

```bash
nano .env
```

Add these values (replace with your actual credentials):

```bash
# Twilio credentials from https://console.twilio.com
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_32_character_auth_token

# Your personal phone number (E.164 format with +)
ALLOWED_PHONE_NUMBERS=+12165448688

# Avigilon door unlock URL
AVIGILON_URL=https://access.alta.avigilon.com/cloudKeyUnlock?shortCode=3m459l66wqvsh
DOOR_BUTTON_TEXT=Mission Sliding Door

# Server configuration
PORT=8000
HOST=0.0.0.0
```

Save and exit (Ctrl+X, then Y, then Enter).

### Step 4: Run Setup Script

This installs Python dependencies and Playwright browsers:

```bash
chmod +x start.sh
./start.sh
```

The script will:
- Create Python virtual environment
- Install all dependencies
- Install Chromium browser for Playwright
- Validate your configuration

This may take 5-10 minutes on Pi.

### Step 5: Authenticate with Avigilon

**Option A: Authenticate on Mac and Transfer**

If you already authenticated on your Mac:

```bash
# On Mac - copy cookies.json to Pi
scp ~/pi-home-server/cookies.json pi@raspberrypi.local:~/pi-home-server/cookies.json
```

**Option B: Authenticate Directly on Pi**

If Pi has a display connected:

```bash
cd ~/pi-home-server
source venv/bin/activate
python auth.py
```

This opens a browser where you log into Avigilon. Cookies are saved to `cookies.json`.

### Step 6: Test Door Opening

Verify everything works:

```bash
cd ~/pi-home-server
source venv/bin/activate
python door.py
```

Expected output:
```
Testing door opener...
============================================================
Status: {'browser_running': True, 'session_valid': True, 'cookies_exist': True}

Attempting to open door...
✓ Success: success
```

If the door opens, you're ready to proceed!

### Step 7: Install as System Service

Set up auto-start on boot:

```bash
# Copy service file
sudo cp pi-home-server.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable pi-home-server

# Start service
sudo systemctl start pi-home-server

# Check status
sudo systemctl status pi-home-server
```

Expected output:
```
● pi-home-server.service - Pi Home Server - SMS Door Opener
   Loaded: loaded (/etc/systemd/system/pi-home-server.service; enabled)
   Active: active (running) since ...
```

View real-time logs:
```bash
sudo journalctl -u pi-home-server -f
```

### Step 8: Install ngrok

Install ngrok to expose your Pi to the internet:

```bash
# Download ngrok for ARM64 (Pi 5)
cd ~
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz

# Extract
tar -xvzf ngrok-v3-stable-linux-arm64.tgz

# Move to system path
sudo mv ngrok /usr/local/bin/

# Configure with your auth token
# Get token from: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### Step 9: Start ngrok Tunnel

```bash
ngrok http 8000
```

You'll see output like:
```
Session Status                online
Forwarding                    https://abc123xyz.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS forwarding URL** (e.g., `https://abc123xyz.ngrok-free.app`)

**Note**: Keep this terminal open! If you close it, the tunnel stops. See "Running ngrok as Service" below for persistent setup.

### Step 10: Configure Twilio Webhook

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/active
2. Click your phone number
3. Scroll to **Messaging Configuration**
4. Under "A MESSAGE COMES IN":
   - Webhook: `https://abc123xyz.ngrok-free.app/sms` (use your ngrok URL)
   - HTTP Method: `POST`
5. Click **Save**

### Step 11: Test via SMS!

Send a text message from your phone (+12165448688) to your Twilio number:

```
door
```

The door should open and you'll receive a reply: `Opening door`

Try the status command:
```
status
```

You should receive: `Server online. Session active.`

### Success! 🎉

Your Pi is now running as an SMS-controlled door opener!

## Usage

### SMS Commands

| Command | Action |
|---------|--------|
| `door` | Opens the mission sliding door |
| `status` | Checks server and session status |

### Example

```
You: door
Pi:  Door opened at 9:42am
```

```
You: status
Pi:  Server online. Session active.
```

## Optional: Running ngrok as Service

By default, ngrok runs in a terminal and stops if you close it. To make it persistent:

### Option A: Simple Screen Session

```bash
# Install screen
sudo apt install screen -y

# Start a detached screen session with ngrok
screen -dmS ngrok ngrok http 8000

# View ngrok output
screen -r ngrok

# Detach: Press Ctrl+A then D
```

After reboot:
```bash
screen -dmS ngrok ngrok http 8000
```

### Option B: ngrok Systemd Service

Create a service file:

```bash
sudo nano /etc/systemd/system/ngrok.service
```

Add:
```ini
[Unit]
Description=ngrok tunnel
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/local/bin/ngrok http 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ngrok
sudo systemctl start ngrok
sudo systemctl status ngrok
```

Check your ngrok URL:
```bash
curl http://localhost:4040/api/tunnels | grep -o 'https://[^"]*ngrok[^"]*'
```

**Note**: With free ngrok, the URL changes on restart. You'll need to update the Twilio webhook each time. For a persistent URL, consider Cloudflare Tunnel or paid ngrok ($8/month).

## Troubleshooting

### SMS Not Working

**Check 1: Is the server running?**
```bash
sudo systemctl status pi-home-server
```

Should show `Active: active (running)`. If not:
```bash
sudo systemctl restart pi-home-server
sudo journalctl -u pi-home-server -f
```

**Check 2: Is ngrok running?**
```bash
curl http://localhost:4040/api/tunnels
```

If this fails, ngrok is not running. Restart it:
```bash
ngrok http 8000
```

**Check 3: Is Twilio webhook configured correctly?**
- Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/active
- Verify webhook URL matches your current ngrok URL
- URL must end with `/sms` and use `POST` method

**Check 4: Is your phone number allowed?**
```bash
cat ~/.env | grep ALLOWED_PHONE_NUMBERS
```

Should match your phone in E.164 format: `+12165448688`

**Check 5: View detailed logs**
```bash
sudo journalctl -u pi-home-server -n 50
```

Look for errors or rejected requests.

### "Session expired" error

Your Avigilon session has expired. Re-authenticate:

```bash
cd ~/pi-home-server
source venv/bin/activate
python auth.py
```

Then restart the service:
```bash
sudo systemctl restart pi-home-server
```

### "Failed to open door" error

**Test the door automation directly:**
```bash
cd ~/pi-home-server
source venv/bin/activate
python door.py
```

If this fails:
1. Check `cookies.json` exists and is valid
2. Check `AVIGILON_URL` and `DOOR_BUTTON_TEXT` in `.env`
3. Try re-authenticating with `python auth.py`

### Button not found

The button text on Avigilon page may have changed. Update `.env`:

```bash
nano ~/.env
```

Change `DOOR_BUTTON_TEXT` to match exact text on the Avigilon page (case-insensitive).

Then restart:
```bash
sudo systemctl restart pi-home-server
```

### Rate limit exceeded

You've sent more than 10 commands in one hour. Wait an hour, or temporarily increase the limit:

```bash
nano ~/pi-home-server/config.py
```

Change `rate_limit_max_requests = 10` to a higher number, then:
```bash
sudo systemctl restart pi-home-server
```

### Pi Can't Install Playwright Browsers

If you get memory errors during Playwright install:

```bash
# Add swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Try installing again
cd ~/pi-home-server
source venv/bin/activate
playwright install chromium
playwright install-deps
```

### ngrok URL Changed

Free ngrok URLs change when you restart ngrok. Update Twilio webhook:

1. Get new URL: `curl http://localhost:4040/api/tunnels | grep public_url`
2. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/active
3. Update webhook to new URL + `/sms`
4. Save

To avoid this, use Cloudflare Tunnel (free, persistent) or paid ngrok.

## Security Notes

- `cookies.json` contains sensitive session data - keep it secure (permissions set to 600)
- Only allowlisted phone numbers can trigger commands
- Unauthorized requests are silently ignored
- Twilio webhook signature validation prevents spoofing
- Never commit `.env` or `cookies.json` to git

## File Structure

```
pi-home-server/
├── main.py              # FastAPI server + Twilio webhook handler
├── door.py              # Playwright automation for door opening
├── auth.py              # Session management + manual login
├── config.py            # Environment variable loader
├── requirements.txt     # Python dependencies
├── .env                 # Secrets (gitignored)
├── cookies.json         # Session cookies (gitignored)
├── TODO.md             # Development checklist
├── CLAUDE.md           # Architecture decisions & best practices
└── README.md           # This file
```

## Useful Commands

### Server Management

```bash
# Check server status
sudo systemctl status pi-home-server

# Restart server
sudo systemctl restart pi-home-server

# Stop server
sudo systemctl stop pi-home-server

# Start server
sudo systemctl start pi-home-server

# View logs (real-time)
sudo journalctl -u pi-home-server -f

# View recent logs
sudo journalctl -u pi-home-server -n 50

# View logs from today
sudo journalctl -u pi-home-server --since today
```

### ngrok Management

```bash
# Check ngrok status
curl http://localhost:4040/api/tunnels

# Get current ngrok URL
curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*ngrok[^"]*'

# Restart ngrok (if running in screen)
screen -r ngrok
# Press Ctrl+C to stop, then restart: ngrok http 8000
```

### Testing

```bash
# Test door opening directly
cd ~/pi-home-server
source venv/bin/activate
python door.py

# Test server is responding
curl http://localhost:8000

# Simulate SMS webhook locally
curl -X POST http://localhost:8000/sms \
  -d "From=+12165448688" \
  -d "Body=status"
```

### Updating Code

```bash
# Pull latest changes from GitHub
cd ~/pi-home-server
git pull

# Restart service to apply changes
sudo systemctl restart pi-home-server
```

## Development

### Testing Locally (Mac/Linux)

```bash
# Test authentication
python auth.py

# Test door opening
python door.py

# Run server with auto-reload
uvicorn main:app --reload

# Simulate Twilio webhook with curl
curl -X POST http://localhost:8000/sms \
  -d "From=+12165448688" \
  -d "Body=door"
```

### Adding New Commands

1. Add command handler in `main.py` under the `/sms` endpoint
2. Update README with new command
3. Test thoroughly before deploying to Pi

## Future Enhancements

- [ ] Multiple doors support
- [ ] Scheduled auto-open (e.g., "unlock at 9am weekdays")
- [ ] Guest mode with temporary access
- [ ] Web dashboard for viewing logs
- [ ] SQLite logging for audit trail
- [ ] PIN code authentication

## License

MIT

## Support

For issues or questions, see `CLAUDE.md` for architectural details or open an issue on GitHub.
