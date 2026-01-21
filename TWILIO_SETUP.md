# Twilio Setup Guide

Complete guide for setting up Twilio to receive SMS messages for your Pi Home Server.

## Step 1: Create Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free trial account
3. Verify your email address
4. Verify your personal phone number (the one you'll text from)

**Important**: During trial, you can only send/receive SMS to/from verified phone numbers. This is perfect for testing!

## Step 2: Get Your Credentials

Once logged in to the Twilio Console:

1. Go to the Dashboard (https://console.twilio.com/)
2. Look for the **Account Info** section
3. You'll see:
   - **Account SID** - starts with "AC..." (copy this)
   - **Auth Token** - click to reveal, then copy

**Save these** - you'll need them for your `.env` file.

## Step 3: Get a Phone Number

### Choosing a Number

**Does it matter which number?** Not really, but:
- ✅ **Get a US number** if you're in the US (lowest latency, best deliverability)
- ✅ **SMS-capable** is required (all modern numbers support this)
- ✅ **Local area code** can be nice but not necessary
- ❌ **Toll-free numbers** work but cost more per SMS
- ❌ **Short codes** are expensive and overkill for this

**Recommendation**: Just get the cheapest US local number in any area code.

### How to Get It

1. In Twilio Console, go to: **Phone Numbers** → **Manage** → **Buy a number**
2. Or direct link: https://console.twilio.com/us1/develop/phone-numbers/manage/search
3. Filter by:
   - **Country**: United States (or your country)
   - **Capabilities**: Check "SMS"
   - **Number type**: Local (cheapest option)
4. Click **Search**
5. Pick any number (they're all the same functionality-wise)
6. Click **Buy** (free during trial, ~$1/month after)
7. Confirm purchase

**Copy your new phone number** - it will be in E.164 format like `+12025551234`

## Step 4: Configure Your Number (WAIT - Do This AFTER Server is Running)

**DON'T DO THIS YET** - You'll configure the webhook URL after we start your server and get an ngrok URL.

But for reference, here's what you'll do later:

1. Go to: **Phone Numbers** → **Manage** → **Active numbers**
2. Click on your phone number
3. Scroll to **Messaging Configuration**
4. Under "A MESSAGE COMES IN":
   - Webhook: `https://your-ngrok-url.ngrok.io/sms` (you'll get this later)
   - HTTP Method: `POST`
5. Click **Save**

## Step 5: Update Your .env File

Now update `~/pi-home-server/.env`:

```bash
# Replace with your actual values:
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
ALLOWED_PHONE_NUMBERS=+12025551234
AVIGILON_URL=https://access.alta.avigilon.com/cloudKeyUnlock?shortCode=PLACEHOLDER
DOOR_BUTTON_TEXT=mission sliding door
PORT=8000
HOST=0.0.0.0
```

**Important**:
- `ALLOWED_PHONE_NUMBERS` should be YOUR personal phone (the one you'll text FROM), not the Twilio number
- Use E.164 format: `+` then country code, then number (no spaces, dashes, or parentheses)
- Example: `+12025551234` not `(202) 555-1234`

## Common Issues & Solutions

### Trial Account Limitations

**Limitation**: Can only text to/from verified numbers
- **Solution**: Verify your personal phone during signup (you should have done this already)
- This is actually perfect for your use case - you only want YOUR phone to work anyway!

**Limitation**: Every SMS says "Sent from your Twilio trial account"
- **Solution**: Upgrade to paid account ($20 credit) to remove this message
- Not necessary for functionality, just looks less polished

### Phone Number Costs

- **Free tier**: Includes $15 credit
- **Number cost**: ~$1/month for local US number
- **SMS cost**: $0.0075 per message sent, $0.0075 per message received
- **Math**: Even with 200 SMS/month, you'd spend ~$4 total

### Geographic Considerations

**US to US**: Works perfectly, use US number
**International**:
- Twilio supports most countries
- Check pricing - international SMS costs more
- Make sure to buy a number in your country for best delivery
- Use correct country code in E.164 format

### Webhook URL Changes

**Problem**: ngrok URLs change every time you restart (unless you have a paid plan)

**Solutions**:
1. **Quick testing**: Just update the webhook URL in Twilio Console each time
2. **Persistent URL**: Use Cloudflare Tunnel (free, doesn't change)
3. **Paid ngrok**: $8/month for static domain
4. **VPS reverse proxy**: Most robust, ~$5/month

For now, we'll use free ngrok and just update the URL each time you test.

## What You'll Need to Copy

Once you're done with Twilio setup, have these ready:

1. ✅ **Account SID** (starts with AC...)
2. ✅ **Auth Token** (32 characters)
3. ✅ **Your Twilio phone number** (E.164 format: +1234567890)
4. ✅ **Your personal phone number** (E.164 format: +1234567890)

## Next Steps

Once your `.env` file is updated with real credentials:

1. Start your server: `uvicorn main:app --reload`
2. Start ngrok: `ngrok http 8000`
3. Configure Twilio webhook with ngrok URL
4. Send test SMS!

---

**Questions?** Just ask! The main thing is getting your credentials and phone number - everything else is straightforward.
