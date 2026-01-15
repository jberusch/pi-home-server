# Claude Development Notes

## Project Overview
SMS-controlled door opener for Raspberry Pi that receives texts via Twilio and automates clicking a door unlock button on the Avigilon web interface.

## Architectural Decisions

### Why FastAPI?
- Lightweight and performant, ideal for Raspberry Pi
- Built-in async support for handling webhooks
- Minimal dependencies compared to Flask + extensions
- Easy request validation and response formatting

### Why Playwright over Selenium?
- Better headless performance on Pi
- More reliable auto-wait mechanisms
- Cleaner API for modern web apps
- Built-in session/cookie management

### File Structure Rationale
```
config.py   → Centralized configuration, validates env vars on startup
auth.py     → Separates session management from business logic
door.py     → Encapsulates browser automation, can be tested independently
main.py     → Thin FastAPI layer, just routing and Twilio integration
```

This separation allows:
- Testing door automation without running the web server
- Reusing auth logic if we add more endpoints
- Easy addition of new SMS commands without touching browser code

## Security Considerations

### Phone Number Allowlist
- Implemented in config.py, checked before any action
- Uses E.164 format (+1234567890) for consistency
- Unauthorized requests are silently ignored (no response) to avoid revealing server existence

### Twilio Webhook Validation
- Validates X-Twilio-Signature header on every request
- Prevents replay attacks and spoofing
- Uses Twilio library's built-in validation (secure implementation)

### Session Management
- cookies.json contains sensitive session data
- Must be gitignored and file permissions restricted (600)
- No credentials stored in code or environment variables
- Session expiry is gracefully handled with SMS notification

### Rate Limiting
- Simple in-memory counter: 10 requests per hour per phone number
- Prevents abuse even from allowlisted numbers
- Resets hourly (not sliding window for simplicity)

## Raspberry Pi Optimization

### Why Headless Chromium?
- Full browser needed for modern web apps (not just HTTP requests)
- Avigilon likely uses JavaScript for authentication and button clicks
- Headless mode reduces memory footprint on Pi

### Memory Considerations
- FastAPI + Playwright will use ~150-300MB RAM
- Pi 5 with 4GB is more than sufficient
- Could add swap if running other services

### Startup Behavior
- Keep browser context alive between requests (don't reinitialize)
- Reuse persistent context with cookies.json
- Only spawn new browser if session expired or server restart

## Error Handling Philosophy

### User-Facing Errors (via SMS)
- "Failed to open door" → Generic, actionable
- "Session expired" → Specific, tells user what to do
- "Unknown command" → Helpful, guides to correct usage

### Internal Errors (logs)
- Detailed stack traces for debugging
- Log all requests with timestamp and sanitized phone number
- Distinguish between expected failures (wrong command) and unexpected (browser crash)

## Testing Strategy

### Manual Testing
1. `python auth.py` → Authenticate once, save cookies
2. `python door.py` → Test door opening independently
3. `uvicorn main:app --reload` → Run server locally
4. Use Twilio test credentials or curl to simulate webhook

### What to Test
- [ ] Valid phone sends "door" → Door opens, confirmation SMS sent
- [ ] Valid phone sends "status" → Status response received
- [ ] Invalid phone sends command → No response (silent ignore)
- [ ] Session expired → Error message sent, door doesn't open
- [ ] Malformed webhook → 400 response, no action taken
- [ ] Rate limit exceeded → Error message sent

## Deployment Notes

### Exposing Pi to Internet
**Option 1: ngrok (easiest for testing)**
```bash
ngrok http 8000
# Update Twilio webhook URL with ngrok URL
```

**Option 2: Cloudflare Tunnel (free, persistent)**
```bash
cloudflared tunnel --url http://localhost:8000
# More reliable than ngrok, won't change URL on restart
```

**Option 3: Reverse proxy via VPS (most robust)**
- Cheapest VPS ($5/mo) as reverse proxy
- Pi connects to VPS via SSH tunnel or Tailscale
- VPS exposes HTTPS endpoint to Twilio

### Running as Service
Create systemd service to auto-start on Pi boot:
```ini
[Unit]
Description=Pi Home Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pi-home-server
ExecStart=/home/pi/pi-home-server/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Future Considerations

### Scaling to Multiple Commands
When adding more commands, consider:
- Command router pattern (dict mapping commands to handlers)
- Separate file for each command handler
- Shared browser context pool

### Database for Logs
Currently in-memory/file logs. If logging becomes important:
- SQLite is perfect for Pi (no separate server needed)
- Track: timestamp, phone, command, success/failure, response_time
- Could enable web dashboard later

### Multiple Users
If expanding beyond Joe's flip phone:
- Add user management system
- Per-user rate limits
- Per-user door permissions
- Consider adding PIN codes for security

## Development Principles
1. **Simplicity over cleverness** - This runs on a Pi, keep it simple
2. **Fail loudly in development, gracefully in production** - Helpful errors for Joe, no info leak to unauthorized users
3. **Stateless where possible** - Only persistent state is cookies.json
4. **Optimize for reliability, not performance** - Door opening is not latency-sensitive
