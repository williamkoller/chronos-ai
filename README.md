# 🤖 CHRONOS AI - Intelligent Time Orchestrator

> Seu assistente de produtividade pessoal com IA local e inteligência instantânea

## ✨ Principais Recursos

- 🧠 **IA Híbrida**: Modo desenvolvimento ultra-rápido + LocalAI para produção
- 📋 **Integração Notion**: Sincronização automática de tarefas
- ⚡ **Respostas Instantâneas**: 0.1s vs 15s+ de outras soluções
- 📊 **Dashboard Interativo**: Interface moderna com Streamlit
- 🎯 **Agendamento Inteligente**: Baseado em categoria, prioridade e padrões
- 📈 **Analytics Avançado**: Padrões de produtividade e otimizações
- 🔄 **Feedback Loop**: Aprendizado contínuo com suas preferências
- 🐳 **Docker Ready**: Setup completo em um comando

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │    │       API       │    │    IA Engine    │
│   (Streamlit)   │◄──►│    (FastAPI)    │◄──►│   (Híbrida)     │
│   Port: 8501    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │  Modo Dev       │
         │                       │              │  (Instantâneo)  │
         │                       │              └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   PostgreSQL    │    │    LocalAI      │
         │              │   (Database)    │    │  (Produção)     │
         │              └─────────────────┘    │   Port: 8080    │
         │                                     └─────────────────┘
         ▼
┌─────────────────┐
│   Notion API    │
│  (Integração)   │
└─────────────────┘
```

## 🚀 Quick Start

### 1. Pré-requisitos

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install docker.io docker-compose make git

# macOS
brew install docker docker-compose make

# Verificar instalação
docker --version && docker-compose --version
```

### 2. Clone e Configure

```bash
git clone <your-repo>
cd chronos-ai

# Setup completo automático
make setup
```

### 3. Configuração Rápida

Edite o arquivo `.env`:

```bash
# Notion Configuration
NOTION_TOKEN=ntn_sua_chave_aqui
DATABASE_ID=sua_database_id_aqui

# IA Configuration (LocalAI)
OPENAI_BASE_URL=http://localai:8080/v1

# Database Configuration
DB_PASSWORD=sua_senha_segura
```

### 4. Iniciar Sistema

```bash
# Comando único para tudo
make up

# URLs disponíveis:
# 📊 Dashboard: http://localhost:8501
# 🔌 API: http://localhost:8000
# 🤖 LocalAI: http://localhost:8080
```

## 🧠 Sistema de IA Híbrido

### Modo Desenvolvimento (Padrão)

- **Velocidade**: Respostas em 0.1 segundos
- **Inteligência**: Algoritmos baseados em regras inteligentes
- **Realismo**: Simula GPT com variações e confiança dinâmica
- **Ideal para**: Desenvolvimento, testes, demonstrações

### Modo Produção (LocalAI)

- **IA Real**: Modelo GPT local rodando no container
- **Privacidade**: 100% local, zero dados enviados externamente
- **Fallback**: Usa modo dev se LocalAI falhar
- **Ideal para**: Produção, uso avançado

### Alternância de Modos

```bash
# Modo Dev (ultra-rápido)
AI_DEV_MODE=true

# Modo Produção (IA real)
AI_DEV_MODE=false
```

## 📋 Comandos Make Disponíveis

```bash
make help          # 📋 Mostra todos os comandos
make setup         # 🔧 Setup inicial completo
make up            # 🚀 Inicia sistema
make down          # 🛑 Para sistema
make restart       # 🔄 Reinicia tudo
make status        # 📊 Status dos serviços
make logs          # 📋 Logs em tempo real
make test          # 🧪 Testa conectividade
make test-ai       # 🤖 Testa especificamente a IA
make clean         # 🧹 Limpeza completa
make backup        # 💾 Backup dos dados
```

## 🔧 Configuração

### Notion Setup

1. Acesse [Notion Developers](https://developers.notion.com)
2. Crie uma integração e copie o token
3. Compartilhe sua database com a integração
4. Copie o ID da database da URL

### Estrutura da Database Notion

```
Propriedades Obrigatórias:
├── Name (title) - Nome da tarefa
├── Category (select) - Categoria
├── Priority (select) - Prioridade
├── Estimated Time (number) - Tempo estimado
├── Status (select) - Status
├── Due Date (date) - Data limite
└── AI Confidence (number) - Confiança da IA
```

## 🎯 Funcionalidades

### 📅 Agendamento Inteligente

- **Análise de Contexto**: Considera horário, categoria, prioridade
- **Padrões Pessoais**: Aprende suas preferências de timing
- **Otimização Automática**: Sugere melhor horário baseado em eficiência
- **Alternativas**: Sempre oferece 2-3 opções diferentes

### 📊 Analytics e Padrões

- **Produtividade por Hora**: Identifica picos de energia
- **Eficiência por Categoria**: Melhor timing para cada tipo de tarefa
- **Tendências**: Tracking de performance ao longo do tempo
- **Recomendações**: Sugestões personalizadas de melhoria

### 🔄 Feedback Loop

- **Avaliação de Sugestões**: Rate as sugestões da IA
- **Ajustes Automáticos**: Sistema aprende com seu feedback
- **Melhoria Contínua**: Precisão aumenta com o uso

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
chronos-ai/
├── api/                    # FastAPI backend
│   └── main.py            # Endpoints principais
├── dashboard/             # Streamlit frontend
│   └── app.py            # Interface do usuário
├── core/                  # Lógica central
│   ├── models.py         # Modelos de dados
│   └── scheduler.py      # Motor de agendamento
├── integrations/          # Integrações externas
│   ├── ai_client.py      # Cliente IA híbrido
│   └── notion_client.py  # Cliente Notion
├── learning/              # Sistema de aprendizado
│   ├── pattern_analyzer.py
│   └── feedback_processor.py
├── localai/               # LocalAI config
│   ├── models/           # Modelos de IA
│   └── config/           # Configurações
├── docker-compose.yml     # Orquestração
├── Makefile              # Automação
└── README.md             # Este arquivo
```

### Modo Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar API
cd api && python main.py

# Executar Dashboard (novo terminal)
cd dashboard && streamlit run app.py

# Executar com Docker (recomendado)
make up
```

### Debugging e Logs

```bash
# Logs específicos
make logs-api      # API logs
make logs-ai       # LocalAI logs

# Debug mode
docker-compose logs -f chronos-api

# Teste de conectividade
make test
```

## 🔒 Privacidade e Segurança

- ✅ **100% Local**: Nenhum dado sai do seu ambiente
- ✅ **Sem Cloud**: IA roda completamente offline
- ✅ **Código Aberto**: Transparência total do funcionamento
- ✅ **Controle Total**: Você possui todos os dados

## 📈 Performance

### Benchmarks Típicos

```
Modo Desenvolvimento:
├── Resposta da IA: ~0.1s
├── Agendamento: ~0.5s
├── Dashboard: ~2s
└── Uso de RAM: ~200MB

Modo Produção (LocalAI):
├── Resposta da IA: ~2-5s
├── Agendamento: ~3-8s
├── Dashboard: ~3-5s
└── Uso de RAM: ~1-2GB
```

### Otimizações

- **Timeouts Inteligentes**: Fallback automático se IA demorar
- **Cache de Padrões**: Resultados em memória para velocidade
- **Lazy Loading**: Componentes carregam sob demanda
- **Streaming**: Respostas em tempo real no dashboard

## 🐛 Troubleshooting

### Problemas Comuns

#### Dashboard com Timeout

```bash
# Verificar status
make status

# Reiniciar API
docker-compose restart chronos-api

# Ver logs
make logs-api
```

#### LocalAI Lento

```bash
# Alternar para modo dev
# No docker-compose.yml: AI_DEV_MODE=true
make restart
```

#### Notion não Conecta

```bash
# Verificar token e database ID
cat .env

# Testar conectividade
curl http://localhost:8000/
```

#### Erros de Memória

```bash
# Limpar sistema
make clean

# Verificar recursos
docker system df
```

## 🔄 Atualizações

### Update do Sistema

```bash
# Puxar atualizações
git pull origin main

# Rebuildar containers
make update

# Verificar mudanças
make status
```

### Update de Modelos

```bash
# Baixar novos modelos (se disponível)
make download-model

# Reset completo
make clean && make setup
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Changelog

### v2.0.0 - Sistema Híbrido

- ✨ Modo desenvolvimento ultra-rápido
- 🔧 Arquitetura híbrida (Dev + LocalAI)
- ⚡ Performance 100x mais rápida
- 🎯 Algoritmos inteligentes simulando GPT
- 📊 Dashboard mais responsivo

### v1.5.0 - LocalAI Integration

- 🤖 Integração LocalAI completa
- 🏠 IA 100% local e privada
- 🔧 Configuração automatizada
- 📈 Melhorias de performance

### v1.0.0 - Release Inicial

- 📋 Integração Notion
- 🎯 Agendamento básico
- 📊 Dashboard Streamlit
- 🐳 Docker support

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Streamlit](https://streamlit.io/) - Dashboard interativo
- [LocalAI](https://localai.io/) - IA local e privada
- [Notion API](https://developers.notion.com/) - Integração de produtividade
- [Docker](https://docker.com/) - Containerização

---

🚀 **Pronto para revolucionar sua produtividade? Execute `make setup && make up` e comece agora!**
