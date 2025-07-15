# 🤖 CHRONOS AI - Intelligent Time Orchestrator

AI-powered task scheduling system that learns your productivity patterns and optimizes your schedule.

## ✨ Features

- **🧠 AI-Powered Scheduling**: Uses Claude LLM for intelligent task placement
- **📊 Pattern Learning**: Analyzes your productivity patterns automatically
- **🔄 Continuous Improvement**: Learns from feedback to improve suggestions
- **📱 Multiple Interfaces**: API, Web Dashboard, and Mobile (coming soon)
- **🔌 Notion Integration**: Seamless integration with your existing workflow

## 🏗️ Architecture

```
chronos-ai/
├── 📁 core/              # Core scheduling engine
├── 📁 integrations/      # External API clients (Notion, Claude)
├── 📁 learning/          # Pattern analysis and feedback processing
├── 📁 api/              # REST API endpoints
├── 📁 dashboard/        # Streamlit web dashboard
└── 📁 mobile/           # Mobile app (future)
```

## 🚀 Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/chronos-ai
cd chronos-ai
```

2. **Set up environment**

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

3. **Run with Docker**

```bash
docker-compose up -d
```

4. **Access the dashboard**

- Dashboard: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Usage

### API Example

```python
import requests

# Schedule a task
task_data = {
    "title": "Review project proposal",
    "category": "Planning",
    "priority": "High",
    "estimated_time": 90
}

response = requests.post("http://localhost:8000/schedule/task", json=task_data)
suggestion = response.json()

print(f"Best time: {suggestion['scheduled_time']}")
print(f"Confidence: {suggestion['confidence']}")
```

### Dashboard Usage

1. Open http://localhost:8501
2. Navigate to "Schedule Task"
3. Fill in task details
4. Get AI-powered suggestion
5. Provide feedback to improve future suggestions

## 🧠 How It Learns

CHRONOS AI uses several learning mechanisms:

1. **Pattern Analysis**: Analyzes your completed tasks to identify productivity patterns
2. **Feedback Processing**: Learns from your ratings and actions on suggestions
3. **Continuous Adaptation**: Adjusts recommendations based on new data
4. **Context Awareness**: Considers factors like time of day, task type, and workload

## 🔧 Configuration

### Notion Setup

1. Create a Notion integration at https://developers.notion.com
2. Share your database with the integration
3. Add these properties to your database:
   - Name (Title)
   - Category (Select)
   - Priority (Select)
   - Status (Select)
   - Estimated Time (Number)
   - Actual Time (Number)
   - Scheduled Time (Date)

### Claude API Setup

1. Get API key from https://console.anthropic.com
2. Add to your .env file

## 📊 Analytics

CHRONOS AI provides detailed analytics:

- Productivity trends over time
- Peak performance hours
- Category efficiency analysis
- Estimation accuracy tracking
- Feedback trends

## 🔮 Roadmap

- [ ] 📱 Mobile app (iOS/Android)
- [ ] 📅 Google Calendar integration
- [ ] 💬 Slack bot interface
- [ ] 🎯 Goal tracking and recommendations
- [ ] 🤝 Team scheduling optimization
- [ ] 🌍 Multi-timezone support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- 📧 Email: support@chronos-ai.com
- 💬 Discord: https://discord.gg/chronos-ai
- 📖 Docs: https://docs.chronos-ai.com

---

Made with ❤️ by the CHRONOS AI team
