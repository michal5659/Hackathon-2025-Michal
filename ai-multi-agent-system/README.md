# AI Multi-Agent Orchestration System

A Python-based multi-agent system using **Azure OpenAI** and **CrewAI** to automate message classification, task creation, and task execution across multiple communication channels (Email, WhatsApp, Microsoft Teams).

## 🎯 Overview

This system leverages AI-driven agents to:
- **Classify** incoming messages from multiple channels
- **Create** actionable tasks based on classification
- **Execute** tasks via IDIT API integration
- **Respond** automatically to users across their preferred channels

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Message Channels                          │
│         Email    │    WhatsApp    │    Teams                 │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────▼──────────────┐
        │  Message Pull Service    │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────┐
        │    Classification Agent   │
        │    (Azure OpenAI)        │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────┐
        │  Task Creation Agent     │
        │    (CrewAI)              │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────┐
        │  Task Execution Agent    │
        │    (IDIT API)            │
        └───────────┬──────────────┘
                    │
        ┌───────────▼──────────────┐
        │   Response to User       │
        └──────────────────────────┘
```

## 🚀 Features

- **Multi-Channel Support**: Email (IMAP/SMTP), WhatsApp Business API, Microsoft Teams
- **AI-Powered Classification**: Azure OpenAI GPT-4 for intelligent message classification
- **Multi-Agent Architecture**: CrewAI agents for specialized tasks
- **Async Processing**: Concurrent message handling with configurable limits
- **IDIT API Integration**: Execute tasks via external API
- **Comprehensive Logging**: Structured logging with Loguru
- **Configuration Management**: Environment-based configuration with Pydantic
- **Error Handling**: Robust retry mechanisms and fallback strategies

## 📁 Project Structure

```
ai-multi-agent-system/
├── agents/
│   ├── __init__.py
│   ├── classification_agent.py      # Message classification
│   ├── task_creation_agent.py       # Task generation
│   └── task_execution_agent.py      # Task execution
├── channels/
│   ├── __init__.py
│   ├── base_channel.py              # Abstract base class
│   ├── email_channel.py             # Email handler
│   ├── whatsapp_channel.py          # WhatsApp handler
│   └── teams_channel.py             # Teams handler
├── services/
│   ├── __init__.py
│   ├── idit_api_client.py           # IDIT API client
│   └── message_pull_service.py      # Message retrieval
├── config/
│   ├── __init__.py
│   └── settings.py                  # Configuration
├── utils/
│   ├── __init__.py
│   └── logger.py                    # Logging setup
├── tests/                           # Test files
├── orchestrator.py                  # Main orchestration logic
├── main.py                          # Application entry point
├── requirements.txt                 # Dependencies
├── .env.example                     # Environment template
└── README.md                        # This file
```

## 📋 Prerequisites

- Python 3.9 or higher
- Azure OpenAI account and API key
- Access to message channels (Email, WhatsApp Business API, Teams)
- IDIT API credentials

## 🔧 Installation

### 1. Clone or Navigate to Project Directory

```powershell
cd "C:\Users\Michal.Kaner\OneDrive - Sapiens\Desktop\Hakahaton\ai-multi-agent-system"
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your configuration:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_MODEL=gpt-4

# IDIT API Configuration
IDIT_API_BASE_URL=https://api.idit.example.com
IDIT_API_KEY=your_idit_api_key_here

# Email Configuration
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_SMTP_SERVER=smtp.gmail.com

# WhatsApp Configuration
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Teams Configuration
TEAMS_WEBHOOK_URL=your_teams_webhook_url
```

## 🎮 Usage

### Run the Application

```powershell
python main.py
```

The system will:
1. Start polling all configured channels
2. Process incoming messages automatically
3. Execute tasks via IDIT API
4. Send responses back to users

### Manual Message Processing

```python
import asyncio
from orchestrator import get_orchestrator

async def process_single_message():
    orchestrator = get_orchestrator()
    
    message = {
        'message_id': 'test-123',
        'channel': 'email',
        'sender': 'customer@example.com',
        'content': 'I want to check my policy status',
        'timestamp': '2025-11-03T10:00:00',
        'metadata': {}
    }
    
    result = await orchestrator.process_message(message)
    print(result)

asyncio.run(process_single_message())
```

## 🧪 Testing

Run tests with pytest:

```powershell
pytest tests/ -v
```

## 📊 Agent Workflows

### Classification Agent
- Receives raw messages from channels
- Uses Azure OpenAI to classify intent
- Extracts customer information and attributes
- Returns structured classification JSON

### Task Creation Agent
- Takes classification results
- Generates IVO JSON for IDIT API
- Maps actions to API endpoints
- Creates executable task definitions

### Task Execution Agent
- Calls IDIT API with task data
- Processes API responses
- Generates user-friendly responses
- Handles errors gracefully

## 🔌 API Integration

### IDIT API Endpoints

The system supports these IDIT API operations:

- `POST /api/v1/policies/inquiry` - Policy inquiries
- `POST /api/v1/claims/submit` - Claim submission
- `GET /api/v1/claims/status/{id}` - Claim status
- `PUT /api/v1/policies/update` - Policy updates
- `GET /api/v1/payments/inquiry` - Payment information

### Channel Webhooks

For real-time message processing:

- **WhatsApp**: Configure webhook in Meta Business Suite
- **Teams**: Set up Bot Framework webhook
- **Email**: Uses IMAP polling by default

## 📝 Configuration

### Adjust Polling Interval

In `.env`:
```env
MESSAGE_POLL_INTERVAL=60  # seconds
```

### Concurrent Task Limit

```env
MAX_CONCURRENT_TASKS=5
```

### Logging Level

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## 🐛 Troubleshooting

### Azure OpenAI Connection Issues

```powershell
# Test Azure OpenAI connection
python -c "from config.settings import settings; print(settings.azure_openai.endpoint)"
```

### Channel Connection Problems

Check your credentials in `.env` and ensure:
- Email: IMAP/SMTP ports are correct (993/587)
- WhatsApp: Access token is valid
- Teams: Webhook URL is configured

### Import Errors

```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🔐 Security Considerations

- Never commit `.env` file to version control
- Use Azure Key Vault for production secrets
- Implement rate limiting for API calls
- Use secure password storage for email credentials
- Validate all incoming webhook payloads

## 🚀 Deployment

### Docker Deployment (Recommended)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:

```powershell
docker build -t ai-multi-agent-system .
docker run -d --env-file .env ai-multi-agent-system
```

### Azure Container Instances

```powershell
az container create `
  --resource-group your-rg `
  --name ai-multi-agent-system `
  --image your-registry/ai-multi-agent-system:latest `
  --environment-variables-file .env
```

## 📈 Monitoring

Logs are stored in `logs/` directory:
- Daily rotation
- 500 MB size limit
- 10-day retention

View logs:

```powershell
Get-Content -Path "logs\app_2025-11-03.log" -Wait
```

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Add tests
4. Submit pull request

## 📄 License

Proprietary - Sapiens Internal Use Only

## 👥 Support

For issues or questions:
- Create an issue in the repository
- Contact the development team
- Check documentation at `/docs`

## 🔄 Future Enhancements

- [ ] Add Slack channel support
- [ ] Implement message queue (RabbitMQ/Kafka)
- [ ] Add monitoring dashboard
- [ ] Implement feedback learning loops
- [ ] Add A/B testing for responses
- [ ] Create admin API for configuration
- [ ] Add multi-language support
- [ ] Implement conversation history tracking

---

**Built with ❤️ using Azure AI and CrewAI**
