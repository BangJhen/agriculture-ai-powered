# 🔐 API Key Setup Guide

## 🚨 Important: Secure Your API Key

Your OpenRouter API key has been removed from the source code for security. Follow these steps to set it up properly:

## 📋 Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Environment File
```bash
# Copy the example file
cp .env.example .env
```

### 3. Get Your API Key
1. Go to [OpenRouter](https://openrouter.ai/keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-or-v1-...`)

### 4. Configure Your .env File
Edit the `.env` file and replace `your_openrouter_api_key_here` with your actual API key:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
OPENROUTER_MODEL=mistralai/mistral-tiny
OPENROUTER_HTTP_REFERER=indonesian-agricultural-chatbot
```

### 5. Verify Setup
```bash
# Test the configuration
python tests/verify_fix.py

# Start the application
./launch.sh
```

## 🔒 Security Best Practices

✅ **DO:**
- Keep your `.env` file private (never commit to git)
- Use different API keys for development/production
- Regularly rotate your API keys
- Monitor your API usage

❌ **DON'T:**
- Share your API keys in chat, email, or code
- Commit `.env` files to version control
- Use production keys for testing
- Leave unused API keys active

## 🛠️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | *(required)* |
| `OPENROUTER_MODEL` | Model to use | `mistralai/mistral-tiny` |
| `OPENROUTER_HTTP_REFERER` | App identifier | `indonesian-agricultural-chatbot` |

## 🔧 Troubleshooting

### "API key not found" Error
- Make sure `.env` file exists in the project root
- Check that `OPENROUTER_API_KEY` is set correctly
- Verify no extra spaces around the API key

### "Invalid API key" Error
- Double-check your API key is correct
- Ensure you're using an OpenRouter key (starts with `sk-or-v1-`)
- Check if your API key is active on OpenRouter

### "Module not found" Error
```bash
pip install python-dotenv
```

## 📁 File Structure
```
your-project/
├── .env                    # ← Your actual API key (DO NOT COMMIT)
├── .env.example           # ← Template file (safe to commit)
├── agricultural_chatbot.py # ← Updated to use environment variables
└── ...
```

## 🎯 Ready to Go!

Once configured, your API key is secure and the application will work exactly as before, but with better security practices! 🌾✨
