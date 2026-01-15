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

## Installation

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/jberusch/pi-home-server.git
cd pi-home-server
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
playwright install-deps  # Install browser dependencies
```

### 3. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your values
nano .env
```

Required environment variables:

```bash
TWILIO_ACCOUNT_SID=AC...           # From Twilio console
TWILIO_AUTH_TOKEN=your_token       # From Twilio console
ALLOWED_PHONE_NUMBERS=+1234567890  # Your phone (E.164 format)
AVIGILON_URL=https://access.alta.avigilon.com/cloudKeyUnlock?shortCode=XXXXXXXX
DOOR_BUTTON_TEXT=mission sliding door
```

### 4. Authenticate with Avigilon

Run the authentication script to log in and save your session:

```bash
python auth.py
```

This will:
1. Open a browser window
2. Navigate to Avigilon
3. Wait for you to log in
4. Save cookies to `cookies.json`

### 5. Test Door Opening

```bash
# Test door automation (uses saved session)
python door.py
```

If successful, you should see:
```
✓ Success: success
```

### 6. Start Server

```bash
# Run server
uvicorn main:app --host 0.0.0.0 --port 8000

# Or use Python directly
python main.py
```

Server will start on `http://0.0.0.0:8000`

### 7. Expose to Internet

Choose one method to make your Pi accessible to Twilio:

#### Option A: ngrok (easiest for testing)

```bash
# Install ngrok
brew install ngrok  # or download from ngrok.com

# Start tunnel
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

#### Option B: Cloudflare Tunnel (free, persistent)

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared-linux-arm64.deb

# Start tunnel
cloudflared tunnel --url http://localhost:8000
```

#### Option C: VPS Reverse Proxy (most robust)

Set up a cheap VPS ($5/mo) as reverse proxy and tunnel from Pi to VPS.

### 8. Configure Twilio Webhook

1. Go to Twilio Console → Phone Numbers → Your Number
2. Under "Messaging", set "A MESSAGE COMES IN" webhook to:
   ```
   https://your-ngrok-url.ngrok.io/sms
   ```
3. Set HTTP method to `POST`
4. Save

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

## Running as Service

To auto-start on boot, create a systemd service:

```bash
sudo nano /etc/systemd/system/pi-home-server.service
```

```ini
[Unit]
Description=Pi Home Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pi-home-server
Environment="PATH=/home/pi/pi-home-server/venv/bin"
ExecStart=/home/pi/pi-home-server/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable pi-home-server
sudo systemctl start pi-home-server
sudo systemctl status pi-home-server
```

View logs:

```bash
sudo journalctl -u pi-home-server -f
```

## Troubleshooting

### "Session expired" error

Re-authenticate:
```bash
cd ~/pi-home-server
source venv/bin/activate
python auth.py
```

### "Failed to open door" error

1. Check if server is running:
   ```bash
   sudo systemctl status pi-home-server
   ```

2. Test door automation directly:
   ```bash
   python door.py
   ```

3. Check logs:
   ```bash
   sudo journalctl -u pi-home-server -f
   ```

### Button not found

Update `DOOR_BUTTON_TEXT` in `.env` to match exact text on Avigilon page.

### Rate limit exceeded

Wait an hour or adjust `rate_limit_max_requests` in `config.py`.

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

## Development

### Testing Locally

```bash
# Test authentication
python auth.py

# Test door opening
python door.py

# Run server with auto-reload
uvicorn main:app --reload

# Simulate Twilio webhook with curl
curl -X POST http://localhost:8000/sms \
  -d "From=+1234567890" \
  -d "Body=door"
```

### Adding New Commands

1. Add command handler in `main.py` under the `/sms` endpoint
2. Update README with new command
3. Test thoroughly

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
