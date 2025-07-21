# 🤖 CHRONOS AI - Intelligent Time Orchestrator

AI-powered task scheduling system que aprende seus padrões de produtividade e otimiza sua agenda usando **IA Local**.

## ✨ Features

- **🧠 IA Local**: Usa Ollama com modelos como Llama 3.2 para agendamento inteligente
- **📊 Análise de Padrões**: Analisa automaticamente seus padrões de produtividade
- **🔄 Melhoria Contínua**: Aprende com feedback para aprimorar sugestões
- **📱 Múltiplas Interfaces**: API, Dashboard Web e Mobile (em breve)
- **🔌 Integração Notion**: Integração perfeita com seu workflow existente
- **🏠 100% Local**: Sem dependências de APIs externas caras

## 🏗️ Arquitetura

```
chronos-ai/
├── 📁 core/              # Motor de agendamento principal
├── 📁 integrations/      # Clientes API (Notion, IA Local)
├── 📁 learning/          # Análise de padrões e processamento de feedback
├── 📁 api/              # Endpoints REST API
├── 📁 dashboard/        # Dashboard web Streamlit
├── 📁 docker-compose.yml # Orquestração completa com Ollama
└── 📁 scripts/          # Scripts de teste e configuração
```

## 🚀 Quick Start

### **Método 1: Docker (Recomendado)**

```bash
# 1. Clone o repositório
git clone https://github.com/yourusername/chronos-ai
cd chronos-ai

# 2. Configure ambiente
cp .env.example .env
# Edite .env com seu token do Notion

# 3. Inicie tudo com Docker
docker-compose up -d

# 4. Configure modelos IA (automático na primeira execução)
# Ollama irá baixar llama3.2:3b automaticamente
```

### **Método 2: Local Development**

```bash
# 1. Instale dependências
pip install -r requirements.txt

# 2. Inicie Ollama localmente
docker run -d -p 11434:11434 --name ollama ollama/ollama
docker exec ollama ollama pull llama3.2:3b

# 3. Configure .env
cp .env.example .env
# Adicione NOTION_TOKEN e DATABASE_ID

# 4. Teste a integração
python test_ai_integration.py

# 5. Inicie API
python api/main.py
```

## 🔧 Configuração

### **Configuração Automática (.env)**

```bash
# Notion Configuration
NOTION_TOKEN=ntn_seu_token_aqui
DATABASE_ID=sua_database_id_aqui

# IA Local Configuration (Ollama)
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b

# Database Configuration
DB_PASSWORD=sua_senha_postgres
```

### **Setup Notion**

```bash
# Execute o script de configuração automática
python setup_notion_database.py

# Ou configure manualmente:
# 1. Crie integração em https://developers.notion.com
# 2. Compartilhe database com a integração
# 3. Execute verificação:
python check_properties.py
```

### **Verificação de IA Local**

```bash
# Teste completo da IA
python test_local_ai.py

# Teste de integração
python test_ai_integration.py

# Setup automático de modelos
python setup_ollama_models.py
```

## 📊 Acesso aos Serviços

Após `docker-compose up -d`:

- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ollama API**: http://localhost:11434

## 📖 Usage

### **API Example**

```python
import requests

# Agendar uma tarefa
task_data = {
    "title": "Revisar proposta do projeto",
    "category": "Planning",
    "priority": "High",
    "estimated_time": 90,
    "description": "Análise detalhada da proposta Q2"
}

response = requests.post("http://localhost:8000/schedule/task", json=task_data)
suggestion = response.json()

print(f"Melhor horário: {suggestion['scheduled_time']}")
print(f"Confiança IA: {suggestion['confidence']}")
print(f"Raciocínio: {suggestion['reasoning']}")
```

### **Dashboard Usage**

1. Abra http://localhost:8501
2. Navegue para "Schedule Task"
3. Preencha detalhes da tarefa
4. Receba sugestão da IA local
5. Forneça feedback para melhorar futuras sugestões

## 🧠 Como Aprende

CHRONOS AI usa mecanismos de aprendizado locais:

1. **Análise de Padrões**: Analisa tarefas concluídas para identificar padrões de produtividade
2. **Processamento de Feedback**: Aprende com suas avaliações e ações
3. **Adaptação Contínua**: Ajusta recomendações baseado em novos dados
4. **Consciência de Contexto**: Considera fatores como hora do dia, tipo de tarefa, carga de trabalho
5. **IA Local**: Usa modelos Llama para sugestões inteligentes sem APIs externas

## 🔧 Modelos IA Disponíveis

### **Modelos Padrão**

- **llama3.2:3b** (Padrão) - Rápido e eficiente (~2GB)
- **mistral:7b** - Equilíbrio qualidade/velocidade (~4GB)
- **codellama:7b** - Especializado em código (~4GB)

### **Trocar Modelo**

```bash
# No .env
OLLAMA_MODEL=mistral:7b

# Ou baixar manualmente
docker exec ollama ollama pull mistral:7b
```

## 🛠️ Scripts de Manutenção

```bash
# Verificar sistema completo
python test_ai_integration.py

# Configurar Notion automaticamente
python setup_notion_database.py

# Verificar propriedades Notion
python check_properties.py

# Diagnosticar Notion
python integrations/notion_diagnostic.py

# Setup modelos Ollama
python setup_ollama_models.py

# Testar IA local
python test_local_ai.py
```

## 📊 Analytics

CHRONOS AI fornece analytics detalhados:

- Tendências de produtividade ao longo do tempo
- Horários de pico de performance
- Análise de eficiência por categoria
- Rastreamento de precisão de estimativas
- Tendências de feedback
- Métricas de IA local

## 🔮 Roadmap

- [x] 🤖 IA Local com Ollama (100% funcional)
- [x] 🔌 Integração Notion completa
- [x] 📊 Dashboard interativo
- [ ] 📱 App Mobile (iOS/Android)
- [ ] 📅 Integração Google Calendar
- [ ] 💬 Bot Slack/Discord
- [ ] 🎯 Tracking de objetivos
- [ ] 🤝 Otimização para equipes
- [ ] 🌍 Suporte multi-timezone
- [ ] 🧠 Modelos IA especializados

## 🚨 Troubleshooting

### **Problemas Comuns**

```bash
# API não conecta
docker logs chronos-ai_chronos-api_1

# Ollama não responde
docker logs chronos-ai_ollama_1
curl http://localhost:11434/api/tags

# Notion não conecta
python test_notion_connection.py

# IA não funciona
python test_ai_integration.py
```

### **Reset Completo**

```bash
docker-compose down -v
docker-compose up -d
python setup_ollama_models.py
```

## 🤝 Contributing

1. Fork o repositório
2. Crie uma branch feature
3. Faça suas mudanças
4. Adicione testes
5. Submeta pull request

## 📄 License

MIT License - veja arquivo LICENSE para detalhes

## 🆘 Support

- 🐛 Issues: GitHub Issues
- 💬 Discussões: GitHub Discussions
- 📖 Docs: README.md (este arquivo)

---

**🎉 Powered by Local AI - Sem APIs externas, sem custos, 100% privado!**

Made with ❤️ by the CHRONOS AI team
