#!/usr/bin/env python3
"""
🤖 TESTE DE IA LOCAL - Chronos AI
Testa conectividade e funcionalidade do Ollama
"""

import os
import sys
import requests
import json
from datetime import datetime

# Carrega variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

def test_ollama_connection():
    """Testa conexão básica com Ollama"""
    ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    
    print("🤖 TESTE DE IA LOCAL - Chronos AI")
    print("=" * 50)
    print(f"🔗 URL Ollama: {ollama_url}")
    
    # 1. Verifica se Ollama está rodando
    print("\n🔍 Verificando status do Ollama...")
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama está rodando!")
            models = response.json().get('models', [])
            print(f"📋 Modelos disponíveis: {len(models)}")
            for model in models:
                print(f"   • {model['name']}")
            return models
        else:
            print(f"❌ Ollama respondeu com erro: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Ollama não está rodando: {e}")
        print("💡 Execute: docker-compose up -d ollama")
        return []

def test_model_generation(model_name="llama3.2:3b"):
    """Testa geração de texto com modelo"""
    ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    
    print(f"\n🧪 Testando geração com modelo: {model_name}")
    
    payload = {
        "model": model_name,
        "prompt": "Você é o Chronos AI, um assistente de agendamento. Responda apenas: Olá! Estou funcionando perfeitamente em modo local.",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9
        }
    }
    
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '').strip()
            
            print(f"✅ Resposta da IA:")
            print(f"   {ai_response}")
            
            # Verifica tempo de resposta
            eval_duration = result.get('eval_duration', 0)
            if eval_duration > 0:
                eval_seconds = eval_duration / 1e9  # nanosegundos para segundos
                print(f"⏱️ Tempo de resposta: {eval_seconds:.2f}s")
            
            return True
        else:
            print(f"❌ Erro na geração: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        return False

def test_chronos_integration():
    """Testa integração com ClaudeClient"""
    print(f"\n🔧 Testando integração Chronos AI...")
    
    # Configura variáveis de ambiente para IA local
    os.environ['OLLAMA_URL'] = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    os.environ['OLLAMA_MODEL'] = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
    
    try:
        # Importa cliente
        sys.path.append('.')
        from integrations.ai_client import AIClient
        
        # Cria cliente IA local
        client = AIClient()  # Não precisa de API key
        
        # Dados de teste
        task_data = {
            "title": "Revisar código Python",
            "category": "Development",
            "estimated_time": 60
        }
        
        user_patterns = {
            "peak_hours": ["09:00-11:00"],
            "productivity_score": 0.8
        }
        
        context = {
            "current_time": datetime.now().isoformat(),
            "workload": "medium"
        }
        
        # Testa geração
        print("🚀 Gerando sugestão de agendamento...")
        suggestion = client.generate_schedule_suggestion(task_data, user_patterns, context)
        
        if suggestion:
            print("✅ Sugestão gerada com sucesso!")
            print(f"   📅 Agendamento: {suggestion.get('scheduled_datetime', 'N/A')}")
            print(f"   🎯 Confiança: {suggestion.get('confidence_score', 'N/A')}")
            print(f"   💭 Reasoning: {suggestion.get('reasoning', 'N/A')[:100]}...")
            return True
        else:
            print("❌ Falha na geração de sugestão")
            return False
            
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False

def main():
    # 1. Testa conexão
    models = test_ollama_connection()
    if not models:
        return 1
    
    # 2. Verifica se tem modelo padrão
    model_names = [m['name'] for m in models]
    if 'llama3.2:3b' in model_names:
        test_model = 'llama3.2:3b'
    elif model_names:
        test_model = model_names[0]
    else:
        print("❌ Nenhum modelo disponível!")
        print("💡 Execute: python setup_ollama_models.py")
        return 1
    
    # 3. Testa geração
    if not test_model_generation(test_model):
        return 1
    
    # 4. Testa integração
    if not test_chronos_integration():
        return 1
    
    print(f"\n🎉 TODOS OS TESTES PASSARAM!")
    print(f"✨ IA Local configurada e funcionando!")
    print(f"📚 Modelo ativo: {test_model}")
    print(f"🚀 Execute: docker-compose up -d para usar!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 