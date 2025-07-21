import requests
import os
import json
from typing import Dict, List, Optional

class NotionDiagnostic:
    """Ferramenta de diagnóstico para problemas de configuração do Notion"""
    
    def __init__(self, token: str, database_id: str):
        self.token = token
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"
    
    def run_full_diagnostic(self) -> Dict:
        """Executa diagnóstico completo"""
        print("🔍 Iniciando diagnóstico da configuração Notion...")
        
        results = {
            "token_validation": self._validate_token(),
            "database_id_format": self._validate_database_id_format(),
            "database_access": self._test_database_access(),
            "database_structure": self._check_database_structure(),
            "recommendations": []
        }
        
        # Gera recomendações
        results["recommendations"] = self._generate_recommendations(results)
        
        # Exibe relatório
        self._display_report(results)
        
        return results
    
    def _validate_token(self) -> Dict:
        """Valida o token do Notion"""
        print("🔐 Validando token de autenticação...")
        
        if not self.token:
            return {
                "status": "error",
                "message": "Token não fornecido",
                "details": "NOTION_TOKEN não está configurado"
            }
        
        if len(self.token) < 50:
            return {
                "status": "warning", 
                "message": "Token parece muito curto",
                "details": f"Token tem {len(self.token)} caracteres, esperado 50+"
            }
        
        # Testa conectividade básica
        try:
            response = requests.get(f"{self.base_url}/users/me", headers=self.headers)
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "status": "success",
                    "message": "Token válido e ativo",
                    "details": f"Conectado como: {user_data.get('name', 'Usuario')} ({user_data.get('type', 'unknown')})"
                }
            elif response.status_code == 401:
                return {
                    "status": "error",
                    "message": "Token inválido ou expirado",
                    "details": "Verifique se o token foi copiado corretamente"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Erro de autenticação: {response.status_code}",
                    "details": response.text[:200]
                }
        except Exception as e:
            return {
                "status": "error",
                "message": "Falha na conexão",
                "details": str(e)
            }
    
    def _validate_database_id_format(self) -> Dict:
        """Valida formato do Database ID"""
        print("📋 Validando formato do Database ID...")
        
        if not self.database_id:
            return {
                "status": "error",
                "message": "Database ID não fornecido",
                "details": "DATABASE_ID não está configurado"
            }
        
        # Remove hífens se existirem
        clean_id = self.database_id.replace("-", "")
        
        if len(clean_id) != 32:
            return {
                "status": "error",
                "message": f"Database ID tem comprimento incorreto: {len(clean_id)} caracteres",
                "details": f"Esperado: 32 caracteres, Encontrado: {len(clean_id)} em '{self.database_id}'"
            }
        
        # Verifica se são caracteres hexadecimais válidos
        try:
            int(clean_id, 16)
            return {
                "status": "success",
                "message": "Formato do Database ID válido",
                "details": f"ID: {self.database_id}"
            }
        except ValueError:
            return {
                "status": "error",
                "message": "Database ID contém caracteres inválidos",
                "details": "Deve conter apenas caracteres hexadecimais (0-9, a-f)"
            }
    
    def _test_database_access(self) -> Dict:
        """Testa acesso ao database"""
        print("🔗 Testando acesso ao database...")
        
        url = f"{self.base_url}/databases/{self.database_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                db_data = response.json()
                return {
                    "status": "success",
                    "message": "Database acessível",
                    "details": {
                        "title": db_data.get("title", [{}])[0].get("text", {}).get("content", "Sem título"),
                        "id": db_data.get("id"),
                        "created_time": db_data.get("created_time"),
                        "last_edited_time": db_data.get("last_edited_time")
                    }
                }
            elif response.status_code == 401:
                return {
                    "status": "error",
                    "message": "Sem permissão para acessar o database",
                    "details": "Verifique se a integração foi adicionada ao database no Notion"
                }
            elif response.status_code == 404:
                return {
                    "status": "error",
                    "message": "Database não encontrado",
                    "details": f"Database ID '{self.database_id}' não existe ou não é acessível"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Erro ao acessar database: {response.status_code}",
                    "details": response.text[:200]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": "Falha na conexão com o database",
                "details": str(e)
            }
    
    def _check_database_structure(self) -> Dict:
        """Verifica estrutura do database"""
        print("🏗️ Verificando estrutura do database...")
        
        url = f"{self.base_url}/databases/{self.database_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": "Não foi possível verificar estrutura",
                    "details": "Database não acessível"
                }
            
            db_data = response.json()
            properties = db_data.get("properties", {})
            
            # Propriedades esperadas pelo sistema
            expected_properties = {
                "Name": "title",
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
            
            missing_properties = []
            wrong_type_properties = []
            found_properties = []
            
            for prop_name, expected_type in expected_properties.items():
                if prop_name not in properties:
                    missing_properties.append(prop_name)
                else:
                    actual_type = properties[prop_name]["type"]
                    if actual_type == expected_type:
                        found_properties.append(prop_name)
                    else:
                        wrong_type_properties.append({
                            "property": prop_name,
                            "expected": expected_type,
                            "actual": actual_type
                        })
            
            status = "success" if not missing_properties and not wrong_type_properties else "warning"
            
            return {
                "status": status,
                "message": f"Estrutura verificada: {len(found_properties)}/{len(expected_properties)} propriedades corretas",
                "details": {
                    "found_properties": found_properties,
                    "missing_properties": missing_properties,
                    "wrong_type_properties": wrong_type_properties,
                    "total_properties": len(properties)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": "Erro ao verificar estrutura",
                "details": str(e)
            }
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Token issues
        if results["token_validation"]["status"] == "error":
            recommendations.append("🔐 Configure um token válido do Notion em NOTION_TOKEN")
            recommendations.append("📖 Acesse https://www.notion.so/my-integrations para criar uma integração")
        
        # Database ID issues  
        if results["database_id_format"]["status"] == "error":
            recommendations.append("📋 Verifique o DATABASE_ID - deve ter 32 caracteres hexadecimais")
            recommendations.append("💡 Para encontrar o ID: abra o database no Notion e copie o ID da URL")
        
        # Access issues
        if results["database_access"]["status"] == "error":
            recommendations.append("🔗 Adicione a integração ao database no Notion")
            recommendations.append("⚙️ No database, clique '...' > 'Add connections' > selecione sua integração")
        
        # Structure issues
        if results["database_structure"]["status"] == "warning":
            missing = results["database_structure"]["details"].get("missing_properties", [])
            if missing:
                recommendations.append(f"🏗️ Adicione as propriedades ausentes: {', '.join(missing)}")
            
            wrong_types = results["database_structure"]["details"].get("wrong_type_properties", [])
            if wrong_types:
                for prop in wrong_types:
                    recommendations.append(f"🔄 Corrija o tipo da propriedade '{prop['property']}': {prop['actual']} → {prop['expected']}")
        
        return recommendations
    
    def _display_report(self, results: Dict):
        """Exibe relatório de diagnóstico"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE DIAGNÓSTICO NOTION")
        print("="*60)
        
        for check_name, result in results.items():
            if check_name == "recommendations":
                continue
                
            status_icon = {
                "success": "✅",
                "warning": "⚠️", 
                "error": "❌"
            }.get(result["status"], "❓")
            
            print(f"\n{status_icon} {check_name.replace('_', ' ').title()}")
            print(f"   {result['message']}")
            
            if isinstance(result.get("details"), dict):
                for key, value in result["details"].items():
                    print(f"   • {key}: {value}")
            elif result.get("details"):
                print(f"   • {result['details']}")
        
        print(f"\n🔧 RECOMENDAÇÕES:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "="*60)


def run_diagnostic():
    """Executa diagnóstico usando variáveis de ambiente"""
    token = os.getenv('NOTION_TOKEN', '')
    database_id = os.getenv('DATABASE_ID', '')
    
    if not token or not database_id:
        print("❌ Configure NOTION_TOKEN e DATABASE_ID antes de executar o diagnóstico")
        return
    
    diagnostic = NotionDiagnostic(token, database_id)
    return diagnostic.run_full_diagnostic()


if __name__ == "__main__":
    run_diagnostic() 