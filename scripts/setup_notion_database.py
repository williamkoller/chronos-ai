#!/usr/bin/env python3
"""
Script para configurar automaticamente o database do Notion
Adiciona todas as propriedades necessárias para o Chronos AI
"""

import os
import sys
import requests
import json

# Tenta importar com fallback
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv não disponível, usando variáveis de ambiente diretas")

def setup_notion_database():
    """Configura o database do Notion com todas as propriedades necessárias"""
    
    token = os.getenv('NOTION_TOKEN', '')
    database_id = os.getenv('DATABASE_ID', '')
    
    if not token or not database_id:
        print("❌ NOTION_TOKEN ou DATABASE_ID não configurados")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    print("🚀 Configurando Database do Notion para Chronos AI")
    print("=" * 60)
    print(f"📋 Database ID: {database_id}")
    print()
    
    # Primeiro, vamos verificar as propriedades existentes
    try:
        print("🔍 Verificando propriedades existentes...")
        response = requests.get(f"https://api.notion.com/v1/databases/{database_id}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar database: {response.status_code}")
            return False
        
        existing_db = response.json()
        existing_properties = existing_db.get("properties", {})
        
        print(f"📊 Propriedades existentes: {len(existing_properties)}")
        for prop_name, prop_info in existing_properties.items():
            prop_type = prop_info.get("type", "unknown")
            print(f"   • {prop_name}: {prop_type}")
        
        # Encontrar qual propriedade é o title
        title_property_name = None
        for prop_name, prop_info in existing_properties.items():
            if prop_info.get("type") == "title":
                title_property_name = prop_name
                break
        
        if title_property_name:
            print(f"✅ Propriedade title encontrada: '{title_property_name}'")
        else:
            print("⚠️ Nenhuma propriedade title encontrada (estranho)")
        
    except Exception as e:
        print(f"❌ Erro ao verificar propriedades existentes: {e}")
        return False
    
    print()
    print("🔨 Definindo propriedades a serem adicionadas...")
    
    # Definição das propriedades necessárias (sem title, pois já existe)
    properties_to_add = {
        "Category": {
            "select": {
                "options": [
                    {"name": "Development", "color": "blue"},
                    {"name": "Meetings", "color": "green"},
                    {"name": "Personal", "color": "purple"},
                    {"name": "Study", "color": "orange"},
                    {"name": "Research", "color": "yellow"},
                    {"name": "Admin", "color": "gray"},
                    {"name": "Creative", "color": "pink"},
                    {"name": "Other", "color": "default"}
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    {"name": "Baixa", "color": "gray"},
                    {"name": "Média", "color": "yellow"},
                    {"name": "Alta", "color": "orange"},
                    {"name": "Urgente", "color": "red"},
                    {"name": "Crítica", "color": "red"}
                ]
            }
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "Pendente", "color": "gray"},
                    {"name": "Em Andamento", "color": "blue"},
                    {"name": "Em Revisão", "color": "yellow"},
                    {"name": "Pausado", "color": "orange"},
                    {"name": "Concluído", "color": "green"},
                    {"name": "Cancelado", "color": "red"}
                ]
            }
        },
        "Estimated Time": {
            "number": {
                "format": "number"
            }
        },
        "Actual Time": {
            "number": {
                "format": "number"
            }
        },
        "Created": {
            "created_time": {}
        },
        "Due Date": {
            "date": {}
        },
        "Scheduled Time": {
            "date": {}
        },
        "Description": {
            "rich_text": {}
        },
        "Tags": {
            "multi_select": {
                "options": [
                    {"name": "ai", "color": "blue"},
                    {"name": "backend", "color": "green"},
                    {"name": "frontend", "color": "orange"},
                    {"name": "bug", "color": "red"},
                    {"name": "feature", "color": "purple"},
                    {"name": "urgent", "color": "red"},
                    {"name": "review", "color": "yellow"},
                    {"name": "documentation", "color": "gray"},
                    {"name": "testing", "color": "pink"},
                    {"name": "refactor", "color": "brown"}
                ]
            }
        }
    }
    
    # Filtrar apenas propriedades que não existem
    properties_to_create = {}
    
    for prop_name, prop_config in properties_to_add.items():
        if prop_name not in existing_properties:
            properties_to_create[prop_name] = prop_config
            print(f"   ➕ Será adicionada: {prop_name}")
        else:
            existing_type = existing_properties[prop_name].get("type")
            expected_type = list(prop_config.keys())[0]
            if existing_type == expected_type:
                print(f"   ✅ Já existe: {prop_name} ({existing_type})")
            else:
                print(f"   ⚠️ Tipo diferente: {prop_name} (tem: {existing_type}, esperado: {expected_type})")
    
    if not properties_to_create:
        print("\n🎉 Todas as propriedades já existem!")
        print("💡 O database já está configurado corretamente")
        return True
    
    print(f"\n📝 Criando {len(properties_to_create)} propriedades...")
    
    # Payload para atualizar o database
    update_payload = {
        "properties": properties_to_create
    }
    
    try:
        print("🔄 Enviando configuração para o Notion...")
        response = requests.patch(
            f"https://api.notion.com/v1/databases/{database_id}",
            headers=headers,
            json=update_payload
        )
        
        if response.status_code == 200:
            print("✅ Database configurado com sucesso!")
            
            # Verifica as propriedades criadas
            updated_db = response.json()
            properties = updated_db.get("properties", {})
            
            print(f"\n🏗️ Propriedades configuradas ({len(properties)}):")
            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get("type", "unknown")
                print(f"   ✅ {prop_name}: {prop_type}")
            
            print(f"\n🎉 CONFIGURAÇÃO COMPLETA!")
            print(f"📊 Total de propriedades: {len(properties)}/11")
            print(f"💡 O Chronos AI agora deve funcionar perfeitamente!")
            
            # Teste rápido de criação de tarefa
            print(f"\n🧪 Testando criação de tarefa exemplo...")
            test_task_creation(headers, database_id, title_property_name)
            
            return True
            
        elif response.status_code == 400:
            error_data = response.json()
            print(f"❌ Erro 400 - Requisição inválida:")
            print(f"   {error_data.get('message', 'Erro desconhecido')}")
            if 'code' in error_data:
                print(f"   Código: {error_data['code']}")
            return False
            
        elif response.status_code == 401:
            print(f"❌ Erro 401 - Token inválido ou sem permissão")
            print(f"   Verifique se o token está correto e se a integração tem acesso ao database")
            return False
            
        elif response.status_code == 404:
            print(f"❌ Erro 404 - Database não encontrado")
            print(f"   Verifique se o DATABASE_ID está correto")
            return False
            
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def test_task_creation(headers, database_id, title_property_name):
    """Testa criação de uma tarefa exemplo"""
    
    # Usar o nome real da propriedade title
    title_prop = title_property_name or "Name"
    
    sample_task = {
        "parent": {"database_id": database_id},
        "properties": {
            title_prop: {
                "title": [{"text": {"content": "🧪 Tarefa de Teste - Chronos AI"}}]
            },
            "Category": {
                "select": {"name": "Development"}
            },
            "Priority": {
                "select": {"name": "Média"}
            },
            "Status": {
                "select": {"name": "Pendente"}
            },
            "Estimated Time": {
                "number": 30
            },
            "Description": {
                "rich_text": [{"text": {"content": "Tarefa criada automaticamente para testar a configuração do Chronos AI. Pode ser removida."}}]
            },
            "Tags": {
                "multi_select": [
                    {"name": "ai"},
                    {"name": "testing"}
                ]
            }
        }
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=sample_task
        )
        
        if response.status_code == 200:
            task_id = response.json()["id"]
            print(f"   ✅ Tarefa de teste criada: {task_id[:8]}...")
        else:
            print(f"   ⚠️ Falha no teste de criação: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️ Erro no teste: {e}")

if __name__ == "__main__":
    print("🤖 CHRONOS AI - Setup Automático do Database Notion")
    print()
    
    success = setup_notion_database()
    
    if success:
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"   1. Execute: python check_properties.py")
        print(f"   2. Reinicie o sistema: docker-compose down && docker-compose up")
        print(f"   3. Teste o agendamento de tarefas!")
    else:
        print(f"\n🔧 RESOLUÇÃO DE PROBLEMAS:")
        print(f"   1. Verifique se o token do Notion está correto")
        print(f"   2. Confirme se a integração foi adicionada ao database")
        print(f"   3. Teste a conectividade: python test_notion_connection.py")
    
    sys.exit(0 if success else 1) 