# LINE Webhook Server Setup Guide

This guide will help you set up and test the LINE webhook server to receive messages from your LINE account.

## Prerequisites

1. ✅ **Dependencies installed** - FastAPI and uvicorn are already added
2. ✅ **Environment variables set** - Your LINE channel credentials are configured
3. ✅ **Server running** - The webhook server is ready at http://localhost:8000

## Step 1: Expose Your Local Server (Choose one method)

### Method A: Using ngrok (Recommended for testing)

1. **Install ngrok**: Visit https://ngrok.com/ and sign up for a free account
2. **Download and install ngrok** for macOS
3. **Authenticate ngrok**:
   ```bash
   ngrok config add-authtoken YOUR_NGROK_TOKEN
   ```
4. **Expose your local server**:
   ```bash
   ngrok http 8000
   ```
5. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### Method B: Using localtunnel
```bash
npm install -g localtunnel
lt --port 8000
```

### Method C: Using serveo (No installation required)
```bash
ssh -R 80:localhost:8000 serveo.net
```

## Step 2: Configure LINE Webhook

1. **Go to LINE Developers Console**: https://developers.line.biz/console/
2. **Select your Messaging API channel**
3. **Go to "Messaging API" tab**
4. **Set Webhook URL**:
   - URL: `https://YOUR_TUNNEL_URL/webhook` (e.g., `https://abc123.ngrok.io/webhook`)
   - Enable "Use webhook"
   - Disable "Auto-reply messages" (optional)
   - Disable "Greeting messages" (optional)

## Step 3: Test the Webhook

1. **Add your bot as a friend** using the QR code in LINE Developers Console
2. **Send a message** to your bot from your LINE account
3. **Check the server logs** - you should see incoming webhook events

## Expected Server Output

When you send "hello" to your bot, you should see:
```
INFO - Received webhook request with 1 events
INFO - Received message event from user: U1234567890abcdef
INFO - User sent text: hello
INFO - Successfully processed webhook with 1 events
```

## Available Test Commands

Send these messages to your bot:
- `hello` - Get a greeting
- `help` - Show available commands
- `status` - Check bot status
- `bye` - Say goodbye
- Send stickers or images to test different message types

## Troubleshooting

### Bot doesn't respond:
1. ✅ Check that your webhook URL is set correctly in LINE Console
2. ✅ Ensure the URL is HTTPS (required by LINE)
3. ✅ Verify your server is running: `curl http://localhost:8000/health`
4. ✅ Check server logs for errors

### Signature verification errors:
1. ✅ Ensure `LINE_CHANNEL_SECRET` matches your channel secret exactly
2. ✅ Check for any extra spaces or characters in your `.env` file

### Server startup errors:
1. ✅ Verify environment variables: `cat .env`
2. ✅ Check dependencies: `uv sync`
3. ✅ Test configuration: `python -c "from line_api import LineAPIConfig; print('Config OK')"`

## Production Deployment

For production, deploy to a cloud service with HTTPS:
- **Heroku**: Easy deployment with automatic HTTPS
- **Railway**: Simple deployment with custom domains
- **Google Cloud Run**: Serverless deployment
- **AWS Lambda**: Serverless with API Gateway
- **DigitalOcean App Platform**: Simple container deployment

## Security Notes

- ✅ **Signature verification is enabled** - Webhooks are authenticated
- ✅ **Environment variables used** - Credentials are not hardcoded
- ✅ **Error handling implemented** - Graceful failure handling
- 🔒 **Use HTTPS in production** - Required by LINE Platform
- 🔒 **Keep credentials secure** - Never commit `.env` to version control

## Next Steps

1. **Customize message handlers** in `examples/webhook_example.py`
2. **Add Flex Messages** for rich interactive content
3. **Implement Rich Menus** for better user experience
4. **Add persistent storage** for user data and conversation state
5. **Deploy to production** with proper monitoring and logging

Happy coding! 🚀
