#!/usr/bin/env python3
"""
🤖 CHRONOS AI - Setup de Modelos Ollama
Configura modelos de IA local para o Chronos AI
"""

import requests
import time
import sys
import json
from typing import List, Dict

class OllamaSetup:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        
    def check_ollama_status(self) -> bool:
        """Verifica se Ollama está rodando"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_available_models(self) -> List[Dict]:
        """Lista modelos disponíveis"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get('models', [])
        except:
            pass
        return []
    
    def pull_model(self, model_name: str) -> bool:
        """Baixa um modelo"""
        print(f"📥 Baixando modelo {model_name}...")
        
        try:
            payload = {"name": model_name}
            response = requests.post(
                f"{self.base_url}/api/pull", 
                json=payload, 
                timeout=600,  # 10 minutos timeout
                stream=True
            )
            
            if response.status_code == 200:
                # Processa resposta stream
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get('status'):
                                print(f"   📊 {data['status']}")
                            if data.get('error'):
                                print(f"   ❌ {data['error']}")
                                return False
                        except:
                            continue
                
                print(f"✅ Modelo {model_name} baixado com sucesso!")
                return True
            else:
                print(f"❌ Erro ao baixar modelo: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao baixar modelo: {e}")
            return False
    
    def test_model(self, model_name: str) -> bool:
        """Testa um modelo"""
        print(f"🧪 Testando modelo {model_name}...")
        
        payload = {
            "model": model_name,
            "prompt": "Responda apenas: Funcionando!",
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                print(f"✅ Modelo responde: {response_text}")
                return True
            else:
                print(f"❌ Erro no teste: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False

def main():
    print("🤖 CHRONOS AI - Setup de Modelos Ollama")
    print("=" * 50)
    
    setup = OllamaSetup()
    
    # Verifica se Ollama está rodando
    print("🔍 Verificando status do Ollama...")
    if not setup.check_ollama_status():
        print("❌ Ollama não está rodando!")
        print("💡 Execute: docker-compose up -d ollama")
        return 1
    
    print("✅ Ollama está rodando!")
    
    # Lista modelos existentes
    existing_models = setup.list_available_models()
    print(f"📋 Modelos já disponíveis: {len(existing_models)}")
    for model in existing_models:
        print(f"   • {model['name']}")
    
    # Modelos recomendados para Chronos AI
    recommended_models = [
        {
            "name": "llama3.2:3b",
            "description": "Pequeno e rápido (3B parâmetros)",
            "size": "~2GB"
        },
        {
            "name": "mistral:7b",
            "description": "Equilibrio qualidade/velocidade (7B parâmetros)",
            "size": "~4GB"
        },
        {
            "name": "codellama:7b",
            "description": "Especializado em código (7B parâmetros)",
            "size": "~4GB"
        }
    ]
    
    print(f"\n🎯 Modelos recomendados para Chronos AI:")
    for i, model in enumerate(recommended_models, 1):
        print(f"   {i}. {model['name']} - {model['description']} ({model['size']})")
    
    # Verifica qual modelo instalar
    existing_names = [m['name'] for m in existing_models]
    
    # Instala llama3.2:3b por padrão se não tiver nenhum
    if 'llama3.2:3b' not in existing_names:
        print(f"\n🚀 Instalando modelo padrão: llama3.2:3b")
        if setup.pull_model('llama3.2:3b'):
            if setup.test_model('llama3.2:3b'):
                print("🎉 Modelo padrão configurado com sucesso!")
            else:
                print("⚠️ Modelo baixado mas teste falhou")
        else:
            print("❌ Falha ao baixar modelo padrão")
            return 1
    else:
        print(f"✅ Modelo padrão já disponível: llama3.2:3b")
        if setup.test_model('llama3.2:3b'):
            print("🎉 Modelo funcionando corretamente!")
    
    print(f"\n✨ Setup concluído!")
    print(f"💡 Para usar outros modelos, edite CLAUDE_MODE=local no .env")
    print(f"📚 Modelos disponíveis: {', '.join(existing_names + ['llama3.2:3b'])}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 