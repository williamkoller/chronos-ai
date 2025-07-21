# 🤖 CHRONOS AI - Makefile
# Automação completa do sistema com IA local
# ==========================================

.PHONY: help install setup up down restart logs clean test status model

# Variáveis
COMPOSE_FILE = docker-compose.yml
MODEL_DIR = localai/models
MODEL_FILE = $(MODEL_DIR)/ggml-gpt4all-j-v1.3-groovy.bin
MODEL_URL = https://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin

# Comando padrão
help: ## 📋 Mostra este menu de ajuda
	@echo "🤖 CHRONOS AI - Automação Completa"
	@echo "=================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "🚀 Uso rápido: make setup && make up"

install: ## 📦 Instala dependências Python
	@echo "📦 Instalando dependências..."
	@pip install -r requirements.txt
	@echo "✅ Dependências instaladas!"

setup: ## 🔧 Setup completo do sistema (primeira vez)
	@echo "🔧 Setup completo do Chronos AI..."
	@make create-dirs
	@make download-model
	@make check-env
	@echo "✅ Setup completo concluído!"

create-dirs: ## 📁 Cria diretórios necessários
	@echo "📁 Criando diretórios..."
	@mkdir -p $(MODEL_DIR) localai/config data
	@echo "✅ Diretórios criados!"

download-model: ## 📥 Baixa modelo de IA local (~3.5GB)
	@if [ ! -f "$(MODEL_FILE)" ]; then \
		echo "📥 Baixando modelo GPT4All (~3.5GB)..."; \
		echo "💡 Isso pode demorar alguns minutos..."; \
		curl -L --progress-bar "$(MODEL_URL)" -o "$(MODEL_FILE)" || \
		(echo "❌ Falha no download!" && rm -f "$(MODEL_FILE)" && exit 1); \
		echo "✅ Modelo baixado com sucesso!"; \
	else \
		echo "✅ Modelo já existe: $(MODEL_FILE)"; \
	fi

check-env: ## 🔍 Verifica arquivo .env
	@if [ ! -f ".env" ]; then \
		echo "⚠️  Arquivo .env não encontrado!"; \
		echo "📝 Criando .env padrão..."; \
		echo "# Chronos AI - Configuração Local\nNOTION_TOKEN=seu_token_aqui\nDATABASE_ID=sua_database_id_aqui\nOPENAI_BASE_URL=http://localai:8080/v1\nDB_PASSWORD=chronos123" > .env; \
		echo "✅ Arquivo .env criado!"; \
		echo "💡 Edite o .env com seus tokens do Notion"; \
	else \
		echo "✅ Arquivo .env encontrado!"; \
	fi

up: ## 🚀 Inicia todo o sistema (IA local + API + Dashboard)
	@echo "🚀 Iniciando Chronos AI completo..."
	@docker-compose up -d
	@echo "⏳ Aguardando serviços ficarem prontos..."
	@sleep 10
	@make status
	@echo ""
	@echo "🎉 Sistema iniciado com sucesso!"
	@echo "📊 Dashboard: http://localhost:8501"
	@echo "🔌 API: http://localhost:8000"
	@echo "🤖 LocalAI: http://localhost:8080"

down: ## 🛑 Para todo o sistema
	@echo "🛑 Parando Chronos AI..."
	@docker-compose down
	@echo "✅ Sistema parado!"

restart: ## 🔄 Reinicia todo o sistema
	@echo "🔄 Reiniciando Chronos AI..."
	@make down
	@sleep 3
	@make up

logs: ## 📋 Mostra logs de todos os serviços
	@echo "📋 Logs do Chronos AI:"
	@docker-compose logs --tail=50 -f

logs-api: ## 📋 Logs apenas da API
	@docker-compose logs --tail=50 -f chronos-api

logs-ai: ## 📋 Logs apenas do LocalAI
	@docker-compose logs --tail=50 -f localai

status: ## 📊 Status de todos os serviços
	@echo "📊 Status dos serviços:"
	@echo "======================="
	@if docker-compose ps | grep -q "Up"; then \
		docker-compose ps; \
		echo ""; \
		echo "🔗 URLs disponíveis:"; \
		echo "   📊 Dashboard: http://localhost:8501"; \
		echo "   🔌 API: http://localhost:8000"; \
		echo "   🤖 LocalAI: http://localhost:8080"; \
		echo "   📖 API Docs: http://localhost:8000/docs"; \
	else \
		echo "❌ Nenhum serviço rodando"; \
		echo "💡 Execute: make up"; \
	fi

test: ## 🧪 Testa conectividade de todos os serviços
	@echo "🧪 Testando conectividade..."
	@echo "=========================="
	@echo -n "📊 Dashboard (8501): "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200" && echo "✅ OK" || echo "❌ FALHA"
	@echo -n "🔌 API (8000): "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200" && echo "✅ OK" || echo "❌ FALHA"
	@echo -n "🤖 LocalAI (8080): "
	@curl -s -o /dev/null -w "%{http_code}" --max-time 60 http://localhost:8080/readyz | grep -q "200" && echo "✅ OK" || echo "❌ FALHA"

test-ai: ## 🤖 Testa especificamente a IA local
	@echo "🤖 Testando IA Local..."
	@echo "======================="
	@curl -X POST http://localhost:8080/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Responda apenas: LocalAI funcionando!"}],"max_tokens":50}' \
		--silent --show-error --max-time 120 | jq -r '.choices[0].message.content' 2>/dev/null || echo "❌ Falha no teste da IA"

clean: ## 🧹 Limpeza completa (remove containers e dados)
	@echo "🧹 Limpeza completa do sistema..."
	@read -p "⚠️  Isso vai remover TODOS os dados! Continuar? [y/N]: " confirm && [ "$$confirm" = "y" ]
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Limpeza concluída!"

clean-model: ## 🗑️ Remove modelo de IA (para re-download)
	@echo "🗑️ Removendo modelo de IA..."
	@rm -f "$(MODEL_FILE)"
	@echo "✅ Modelo removido! Execute 'make download-model' para baixar novamente"

dev: ## 🔧 Modo desenvolvimento (rebuild + logs)
	@echo "🔧 Iniciando modo desenvolvimento..."
	@docker-compose up --build -d
	@make logs

quick-start: ## ⚡ Início rápido completo (setup + up + test)
	@echo "⚡ Início rápido do Chronos AI!"
	@echo "=============================="
	@make setup
	@make up
	@sleep 15
	@make test
	@echo ""
	@echo "🎉 Chronos AI pronto para uso!"

backup: ## 💾 Backup dos dados
	@echo "💾 Fazendo backup..."
	@mkdir -p backup/$(shell date +%Y%m%d_%H%M%S)
	@docker-compose exec -T chronos-db pg_dump -U chronos chronos > backup/$(shell date +%Y%m%d_%H%M%S)/database.sql
	@cp .env backup/$(shell date +%Y%m%d_%H%M%S)/
	@echo "✅ Backup salvo em backup/$(shell date +%Y%m%d_%H%M%S)/"

update: ## 🔄 Atualiza e reinicia o sistema
	@echo "🔄 Atualizando sistema..."
	@git pull
	@make down
	@docker-compose build --no-cache
	@make up

# Aliases para comandos comuns
start: up ## 🚀 Alias para 'up'
stop: down ## 🛑 Alias para 'down'
ps: status ## 📊 Alias para 'status'

# Meta targets
all: setup up test ## 🎯 Setup completo + inicialização + teste 