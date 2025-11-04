# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Setup Environment

```powershell
# Navigate to project
cd "C:\Users\Michal.Kaner\OneDrive - Sapiens\Desktop\Hakahaton\ai-multi-agent-system"

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Credentials

1. Copy the example environment file:
```powershell
Copy-Item .env.example .env
```

2. Edit `.env` with your credentials:
   - Azure OpenAI API key and endpoint
   - Email IMAP/SMTP credentials
   - WhatsApp Business API token (if available)
   - Teams webhook URL (if available)
   - IDIT API credentials

**Minimum Required Configuration:**
```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
IDIT_API_BASE_URL=https://api.idit.example.com
IDIT_API_KEY=your_idit_key
```

### Step 3: Test the Setup

Run the example scripts to verify everything works:

```powershell
python examples.py
```

### Step 4: Start the System

```powershell
python main.py
```

The system will start polling for messages and processing them automatically!

## 📝 Test with Sample Messages

### Email Test
Send an email to your configured email address with content like:
```
Subject: Policy Inquiry

I would like to know the status of my policy #POL-12345
```

### WhatsApp Test
Send a WhatsApp message:
```
I need to submit a claim for my car accident yesterday
```

### Teams Test
Post in your configured Teams channel:
```
What is my next payment due date?
```

## 🔍 Monitor the System

Watch the logs in real-time:
```powershell
Get-Content -Path "logs\app_*.log" -Wait -Tail 50
```

## 🛠️ Common Issues

### Issue: Azure OpenAI Connection Error
**Solution:** Verify your endpoint URL and API key in `.env`

### Issue: Email Authentication Failed
**Solution:** 
- For Gmail: Enable "App Passwords" in Google Account settings
- Use the app password instead of your regular password

### Issue: Module Not Found
**Solution:**
```powershell
pip install -r requirements.txt --force-reinstall
```

## 📖 Next Steps

1. Review the `README.md` for detailed documentation
2. Check `examples.py` for usage patterns
3. Customize agents in `agents/` directory
4. Add custom channel handlers in `channels/`
5. Modify orchestration logic in `orchestrator.py`

## 💡 Tips

- Start with just Email channel to test the system
- Add WhatsApp and Teams once Email is working
- Monitor logs to understand the message flow
- Use `LOG_LEVEL=DEBUG` in `.env` for detailed logging
- Adjust `MESSAGE_POLL_INTERVAL` for faster/slower polling

## 🆘 Need Help?

Check the logs first:
```powershell
Get-Content "logs\app_$(Get-Date -Format 'yyyy-MM-dd').log"
```

Run tests:
```powershell
pytest tests/ -v
```

## ✅ Success Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Azure OpenAI credentials valid
- [ ] Email credentials working
- [ ] IDIT API accessible
- [ ] System starts without errors
- [ ] Test message processed successfully

---

**You're all set! Your AI Multi-Agent Orchestration System is ready to process messages! 🎉**
