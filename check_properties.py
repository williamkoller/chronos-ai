#!/usr/bin/env python3
"""
Script simples para verificar propriedades do database Notion
Execute após adicionar as propriedades necessárias
"""

import os
import sys

# Adiciona o diretório do projeto ao path
sys.path.append('/home/william/development-python/chronos-ai')

# Tenta importar com fallback
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv não disponível, usando variáveis de ambiente diretas")

try:
    import requests
except ImportError:
    print("❌ requests não instalado. Execute: pip install requests")
    sys.exit(1)

def check_database_properties():
    """Verifica se todas as propriedades necessárias estão configuradas"""
    
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
    
    print("🔍 Verificando propriedades do database...")
    print("=" * 50)
    
    try:
        response = requests.get(f"https://api.notion.com/v1/databases/{database_id}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar database: {response.status_code}")
            return False
        
        db = response.json()
        properties = db.get("properties", {})
        
        # Primeiro, encontrar a propriedade title existente
        title_property_name = None
        for prop_name, prop_info in properties.items():
            if prop_info.get("type") == "title":
                title_property_name = prop_name
                break
        
        # Propriedades obrigatórias com tipos esperados
        required_properties = {
            "Category": "select", 
            "Priority": "select",
            "Status": "select",
            "Estimated Time": "number",
            "Actual Time": "number",
            "Created": "created_time",
            "Due Date": "date",
            "Scheduled Time": "date", 
            "Description": "rich_text",
            "Tags": "multi_select"
        }
        
        # Adicionar a propriedade title com seu nome real
        if title_property_name:
            required_properties[title_property_name] = "title"
        
        print(f"📋 Database ID: {database_id}")
        print(f"🏗️ Propriedades encontradas: {len(properties)}")
        print()
        
        missing = []
        wrong_type = []
        correct = []
        
        for prop_name, expected_type in required_properties.items():
            if prop_name in properties:
                actual_type = properties[prop_name]["type"]
                if actual_type == expected_type:
                    correct.append(prop_name)
                    print(f"✅ {prop_name}: {actual_type}")
                else:
                    wrong_type.append((prop_name, expected_type, actual_type))
                    print(f"⚠️ {prop_name}: {actual_type} (esperado: {expected_type})")
            else:
                missing.append(prop_name)
                print(f"❌ {prop_name}: AUSENTE (tipo esperado: {expected_type})")
        
        print()
        print("📊 RESUMO:")
        print(f"✅ Corretas: {len(correct)}/{len(required_properties)}")
        print(f"❌ Ausentes: {len(missing)}")
        print(f"⚠️ Tipo incorreto: {len(wrong_type)}")
        
        if missing:
            print(f"\n🔧 ADICIONE ESTAS PROPRIEDADES:")
            for prop in missing:
                prop_type = required_properties[prop]
                print(f"   • {prop} → Tipo: {prop_type}")
        
        if wrong_type:
            print(f"\n🔄 CORRIJA ESTES TIPOS:")
            for prop, expected, actual in wrong_type:
                print(f"   • {prop}: {actual} → {expected}")
        
        if not missing and not wrong_type:
            print("\n🎉 TODAS AS PROPRIEDADES ESTÃO CORRETAS!")
            print("💡 O Chronos AI deve funcionar perfeitamente agora")
            return True
        else:
            print(f"\n❌ CONFIGURAÇÃO INCOMPLETA")
            print("📖 Siga as instruções acima para corrigir")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

if __name__ == "__main__":
    success = check_database_properties()
    sys.exit(0 if success else 1) 