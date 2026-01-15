# TODO - Pi Home Server

## Project Setup
- [x] Initialize GitHub repository
- [x] Create .env.example
- [x] Create .gitignore
- [x] Create requirements.txt
- [x] Create CLAUDE.md documentation

## Core Implementation
- [x] Implement config.py
  - [x] Load environment variables
  - [x] Validate required config values
  - [x] Parse allowed phone numbers list

- [x] Implement auth.py
  - [x] Session cookie persistence (save/load from cookies.json)
  - [x] Session validation logic
  - [x] Manual authentication flow for initial setup

- [x] Implement door.py
  - [x] Playwright browser setup (headless Chromium)
  - [x] Navigate to Avigilon URL
  - [x] Find and click door button by text
  - [x] Error handling and retry logic
  - [x] Session expiry detection

- [x] Implement main.py
  - [x] FastAPI server setup
  - [x] POST /sms endpoint
  - [x] Twilio webhook signature validation
  - [x] Phone number allowlist checking
  - [x] Command parsing (door, status)
  - [x] TwiML response generation
  - [x] Rate limiting (10 requests/hour)

## Documentation
- [x] Create README.md
  - [x] Overview and architecture
  - [x] Setup instructions
  - [x] Environment variables reference
  - [x] Testing guide
  - [x] Troubleshooting

## Testing & Deployment (Next Steps)
- [ ] Test Playwright automation locally
- [ ] Test FastAPI endpoints
- [ ] Verify Twilio webhook integration
- [ ] Set up ngrok/Cloudflare Tunnel for internet exposure

## Future Enhancements (v2)
- Multiple doors support
- Scheduled auto-open
- Guest mode with temporary access
- Web dashboard for logs
