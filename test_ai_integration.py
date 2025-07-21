#!/usr/bin/env python3
"""
🤖 TESTE DE INTEGRAÇÃO IA - Chronos AI
Testa se a integração IA local está funcionando corretamente
"""

import os
import sys
from datetime import datetime

# Carrega variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

def test_ai_integration():
    """Testa integração completa da IA"""
    print("🤖 TESTE DE INTEGRAÇÃO IA - Chronos AI")
    print("=" * 50)
    
    try:
        # Importa AIClient
        sys.path.append('.')
        from integrations.ai_client import AIClient
        
        print("✅ AIClient importado com sucesso")
        
        # Cria cliente
        ai = AIClient()
        print("✅ AIClient inicializado")
        
        # Dados de teste
        task_data = {
            "title": "Revisar código Python",
            "category": "Development", 
            "estimated_time": 90
        }
        
        user_patterns = {
            "peak_hours": ["09:00-11:00"],
            "productivity_score": 0.8
        }
        
        context = {
            "current_time": datetime.now().isoformat(),
            "workload": "medium"
        }
        
        # Testa geração de sugestão
        print("\n🚀 Testando geração de sugestão...")
        suggestion = ai.generate_schedule_suggestion(task_data, user_patterns, context)
        
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
        import traceback
        print(traceback.format_exc())
        return False

def test_scheduler_integration():
    """Testa integração com o Scheduler"""
    print(f"\n🔧 Testando integração com Scheduler...")
    
    try:
        # Importa ChronosCore
        sys.path.append('.')
        from core.scheduler import ChronosCore
        
        # Configuração mínima
        config = {
            'notion_token': os.getenv('NOTION_TOKEN', ''),
            'database_id': os.getenv('DATABASE_ID', '')
        }
        
        # Inicializa Chronos
        chronos = ChronosCore(config)
        print("✅ ChronosCore inicializado")
        
        # Testa orquestração
        task_data = {
            "title": "Teste integração IA",
            "category": "Testing",
            "priority": "High",
            "estimated_time": 60
        }
        
        print("🚀 Testando orquestração completa...")
        result = chronos.orchestrate_schedule(task_data)
        
        if result and result.get('suggestion'):
            print("✅ Orquestração funcionando!")
            print(f"   📊 Confiança: {result.get('confidence', 'N/A')}")
            print(f"   🎯 Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
            return True
        else:
            print("❌ Falha na orquestração")
            return False
            
    except Exception as e:
        print(f"❌ Erro no scheduler: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    # 1. Testa IA isolada
    if not test_ai_integration():
        print("\n❌ TESTE FALHOU: Problema na IA")
        return 1
    
    # 2. Testa integração completa
    if not test_scheduler_integration():
        print("\n❌ TESTE FALHOU: Problema no Scheduler")
        return 1
    
    print(f"\n🎉 TODOS OS TESTES PASSARAM!")
    print(f"✨ IA Local integrada e funcionando!")
    print(f"🚀 Sistema Chronos AI pronto para uso!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 