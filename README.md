# OpenClaw Clone (Python Agentic AI)

This is a custom-built, lightweight Python AI Agent that mimics the functionality of OpenClaw. It uses **Google Gemini** for reasoning and can autonomously execute tools like searching the web and sending emails via Telegram. 

It is specifically designed to be easily hosted on platforms like **Render**.

## Features
- **Telegram Interface**: Chat with the bot via the Telegram App.
- **Web Search**: Uses DuckDuckGo to answer queries about recent events.
- **Send Emails**: Uses SMTP to send emails directly from chats.
- **Render Ready**: Includes a background Dummy Web Server (`Flask`) to bind to Render's port, keeping the Telegram Polling loop active 24/7 without crashing.

## Deployment on Render

1. Upload this entire repository/folder to your GitHub account.
2. Go to [Render](https://render.com) and create a new **Web Service**.
3. Connect your GitHub repository.
4. Set the **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
5. Set the **Start Command**:
   ```bash
   gunicorn main:flask_app
   ```
   *(Alternatively, if using the included Procfile, Render should detect it automatically).*

6. Add the following **Environment Variables** in the Render Dashboard:
   - `TELEGRAM_TOKEN`: Your bot token from @BotFather on Telegram.
   - `GEMINI_API_KEY`: Your API Key from Google AI Studio.
   - `EMAIL_USER`: The email address you want the bot to send emails from (e.g., `youremail@gmail.com`).
   - `EMAIL_PASS`: The 16-character App Password for your email (if using Gmail, generate this in Google Account Security settings).

7. Click **Deploy**.

## How it works
The `main.py` file runs two processes:
1. A background thread running the `python-telegram-bot` application.
2. The main thread running a simple `Flask` web server to satisfy Render's health checks.

When you message the bot, `agent.py` sends the text to Gemini, providing it with the list of tools defined in `tools.py`. If Gemini decides a tool is needed, the script executes it and returns the result to Gemini, which then formats the final response for Telegram.
