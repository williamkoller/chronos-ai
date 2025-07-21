#!/usr/bin/env python3
"""
Teste específico para criação de tarefas no Notion
Para identificar por que as tarefas não estão sendo enviadas
"""

import os
import sys
import json

# Adiciona o path do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_task_creation():
    """Testa criação de tarefa no Notion"""
    
    # Simula dados como vem do dashboard
    task_data = {
        'title': 'Teste de Criação - Dashboard',
        'category': 'Development', 
        'priority': 'Média',
        'estimated_time': 60,
        'description': 'Tarefa criada via dashboard para testar integração'
    }
    
    schedule_info = {
        'scheduled_datetime': '2025-01-21T14:00:00',
        'confidence_score': 0.8,
        'reasoning': 'Horário ideal para desenvolvimento com base em padrões'
    }
    
    print("🧪 TESTE DE CRIAÇÃO DE TAREFA")
    print("=" * 50)
    print(f"📋 Dados da tarefa:")
    print(json.dumps(task_data, indent=2, ensure_ascii=False))
    print(f"\n⏰ Informações de agendamento:")
    print(json.dumps(schedule_info, indent=2, ensure_ascii=False))
    
    # Verifica variáveis de ambiente
    token = os.getenv('NOTION_TOKEN', '')
    database_id = os.getenv('DATABASE_ID', '')
    
    if not token or not database_id:
        print("\n❌ Configuração incompleta:")
        print(f"   NOTION_TOKEN: {'✅' if token else '❌'}")
        print(f"   DATABASE_ID: {'✅' if database_id else '❌'}")
        return False
    
    try:
        # Importa e testa NotionClient
        from integrations.notion_client import NotionClient
        
        print(f"\n🔗 Conectando ao Notion...")
        notion = NotionClient(token, database_id)
        
        print(f"🚀 Criando tarefa...")
        task_id = notion.create_task(task_data, schedule_info)
        
        if task_id:
            print(f"✅ Tarefa criada com sucesso!")
            print(f"📝 ID da tarefa: {task_id}")
            return True
        else:
            print(f"❌ Falha na criação da tarefa")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Execute dentro do ambiente do projeto")
        return False
    except Exception as e:
        print(f"❌ Erro na criação: {e}")
        return False

def check_api_connectivity():
    """Verifica conectividade básica com API"""
    
    print("\n🔍 VERIFICAÇÃO DE CONECTIVIDADE")
    print("=" * 50)
    
    token = os.getenv('NOTION_TOKEN', '')
    database_id = os.getenv('DATABASE_ID', '')
    
    if not token or not database_id:
        print("❌ Variáveis de ambiente não configuradas")
        return False
    
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Teste 1: Verificar autenticação
        print("🔐 Testando autenticação...")
        response = requests.get("https://api.notion.com/v1/users/me", headers=headers)
        if response.status_code == 200:
            print("✅ Autenticação OK")
        else:
            print(f"❌ Falha na autenticação: {response.status_code}")
            return False
        
        # Teste 2: Verificar acesso ao database
        print("📋 Testando acesso ao database...")
        response = requests.get(f"https://api.notion.com/v1/databases/{database_id}", headers=headers)
        if response.status_code == 200:
            db_data = response.json()
            properties = db_data.get("properties", {})
            print(f"✅ Database acessível ({len(properties)} propriedades)")
            
            # Mostra propriedades
            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get("type", "unknown")
                print(f"   • {prop_name}: {prop_type}")
                
        else:
            print(f"❌ Falha no acesso ao database: {response.status_code}")
            return False
            
        return True
        
    except ImportError:
        print("❌ Biblioteca 'requests' não disponível")
        return False
    except Exception as e:
        print(f"❌ Erro na conectividade: {e}")
        return False

if __name__ == "__main__":
    print("🤖 CHRONOS AI - Teste de Criação de Tarefas")
    print()
    
    # Carrega variáveis de ambiente
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Variáveis de ambiente carregadas")
    except ImportError:
        print("⚠️ python-dotenv não disponível, usando variáveis do sistema")
    
    # Executa testes
    connectivity_ok = check_api_connectivity()
    
    if connectivity_ok:
        print()
        creation_ok = test_task_creation()
        
        if creation_ok:
            print(f"\n🎉 TODOS OS TESTES PASSARAM!")
            print(f"💡 A integração está funcionando corretamente")
        else:
            print(f"\n❌ FALHA NA CRIAÇÃO DE TAREFA")
            print(f"🔧 Verifique os logs acima para mais detalhes")
    else:
        print(f"\n❌ FALHA NA CONECTIVIDADE")
        print(f"🔧 Corrija a conectividade antes de testar criação")
    
    sys.exit(0 if connectivity_ok and creation_ok else 1) 