#!/usr/bin/env python3
"""
Script rápido para testar conectividade com Notion
Use quando quiser verificar se as configurações estão corretas
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Carrega variáveis do .env se existir
load_dotenv()

def test_notion_connection():
    """Testa conectividade básica com Notion"""
    
    # Obtém configurações
    token = os.getenv('NOTION_TOKEN', '')
    database_id = os.getenv('DATABASE_ID', '')
    
    print("🔍 Teste de Conectividade Notion - Chronos AI")
    print("=" * 50)
    
    # Validação básica
    if not token:
        print("❌ NOTION_TOKEN não configurado")
        print("💡 Configure no arquivo .env ou variável de ambiente")
        return False
    
    if not database_id:
        print("❌ DATABASE_ID não configurado")
        print("💡 Configure no arquivo .env ou variável de ambiente")
        return False
    
    print(f"✓ Token presente: {len(token)} caracteres")
    print(f"✓ Database ID: {database_id}")
    
    # Headers para API
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Teste 1: Autenticação
    print("\n🔐 Testando autenticação...")
    try:
        response = requests.get("https://api.notion.com/v1/users/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Conectado como: {user.get('name', 'Usuário')}")
        else:
            print(f"❌ Falha na autenticação: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # Teste 2: Acesso ao Database
    print("\n📋 Testando acesso ao database...")
    try:
        response = requests.get(f"https://api.notion.com/v1/databases/{database_id}", headers=headers)
        if response.status_code == 200:
            db = response.json()
            
            # Extração defensiva do título
            try:
                title_array = db.get("title", [])
                if title_array and len(title_array) > 0:
                    title = title_array[0].get("text", {}).get("content", "Sem título")
                else:
                    title = "Database sem título"
            except (IndexError, KeyError, TypeError) as e:
                title = f"Erro ao extrair título: {type(e).__name__}"
            
            print(f"✅ Database acessível: {title}")
            
            # Debug: mostra estrutura do título
            print(f"🔍 Estrutura do título: {db.get('title', 'Campo title ausente')}")
            
            # Mostra propriedades encontradas
            properties = db.get("properties", {})
            print(f"✓ {len(properties)} propriedades encontradas")
            
            # Verifica propriedades essenciais
            essential = ["Name", "Category", "Priority", "Status"]
            found_essential = [prop for prop in essential if prop in properties]
            print(f"✓ Propriedades essenciais: {len(found_essential)}/{len(essential)}")
            
            if len(found_essential) < len(essential):
                missing = [prop for prop in essential if prop not in properties]
                print(f"⚠️ Propriedades ausentes: {', '.join(missing)}")
            
        elif response.status_code == 404:
            print(f"❌ Database não encontrado")
            print(f"💡 Verifique se o ID está correto: {database_id}")
            return False
        elif response.status_code == 403:
            print(f"❌ Sem permissão para acessar o database")
            print(f"💡 Adicione a integração ao database no Notion")
            return False
        else:
            print(f"❌ Erro no acesso: {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # Teste 3: Query básica
    print("\n📋 Testando query de tarefas...")
    try:
        query_payload = {
            "page_size": 1
        }
        response = requests.post(
            f"https://api.notion.com/v1/databases/{database_id}/query", 
            headers=headers, 
            json=query_payload
        )
        if response.status_code == 200:
            results = response.json().get("results", [])
            print(f"✅ Query executada com sucesso: {len(results)} resultado(s)")
        else:
            print(f"⚠️ Problema na query: {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
    except Exception as e:
        print(f"⚠️ Erro na query: {e}")
    
    print("\n🎉 Conectividade básica confirmada!")
    print("💡 O Chronos AI deve funcionar corretamente agora")
    return True

if __name__ == "__main__":
    try:
        success = test_notion_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Teste interrompido pelo usuário")
        sys.exit(1) 