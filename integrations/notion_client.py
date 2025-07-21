from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional

class NotionClient:
    """Cliente para integração com Notion API"""
    
    def __init__(self, token: str, database_id: str):
        self.token = token
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"
        self.title_property_name = None  # Will be detected on first use
    
    def get_tasks(self, days_back: int = 30) -> List[Dict]:
        """Busca tarefas do Notion"""
        url = f"{self.base_url}/databases/{self.database_id}/query"
        
        filter_payload = {
            "filter": {
                "property": "Created",
                "date": {
                    "after": (datetime.now() - timedelta(days=days_back)).isoformat()
                }
            },
            "sorts": [{"property": "Created", "direction": "descending"}]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=filter_payload)
            if response.status_code == 200:
                return self._parse_notion_response(response.json())
            elif response.status_code == 401:
                print(f"🔐 Notion: Token de autenticação inválido ou expirado")
                return []
            elif response.status_code == 400:
                print(f"📋 Notion: Configuração de database incorreta (ID: {self.database_id[:8]}...)")
                return []
            elif response.status_code == 404:
                print(f"🔍 Notion: Database não encontrado ou sem acesso")
                return []
            else:
                print(f"🌐 Notion API erro {response.status_code}: {response.text[:100]}")
                return []
        except requests.exceptions.ConnectionError:
            print(f"🔌 Notion: Falha de conexão - verifique internet")
            return []
        except requests.exceptions.Timeout:
            print(f"⏱️ Notion: Timeout na requisição")
            return []
        except Exception as e:
            print(f"⚠️ Notion erro inesperado: {type(e).__name__}: {str(e)[:100]}")
            return []
    
    def create_task(self, task_data: Dict, schedule_info: Dict) -> Optional[str]:
        """Cria nova tarefa no Notion"""
        url = f"{self.base_url}/pages"
        
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": self._build_task_properties(task_data, schedule_info)
        }
        
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                task_id = response.json()['id']
                print(f"✅ Tarefa criada no Notion: {task_id}")
                return task_id
            else:
                print(f"❌ Erro ao criar tarefa: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"📋 Detalhes do erro: {error_detail}")
                except:
                    print(f"📋 Resposta do erro: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"❌ Erro na criação: {e}")
            return None
    
    def update_task(self, task_id: str, updates: Dict) -> bool:
        """Atualiza tarefa existente"""
        url = f"{self.base_url}/pages/{task_id}"
        
        payload = {"properties": self._build_update_properties(updates)}
        
        try:
            response = requests.patch(url, headers=self.headers, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Erro na atualização: {e}")
            return False
    
    def get_today_tasks(self) -> List[Dict]:
        """Busca tarefas agendadas para hoje"""
        today = datetime.now().strftime('%Y-%m-%d')
        # Implementa filtro por data
        return self.get_tasks(1)  # Simplificado
    
    def _get_title_property_name(self) -> str:
        """Detecta automaticamente qual propriedade é o title do database"""
        if self.title_property_name is not None:
            return self.title_property_name
        
        try:
            response = requests.get(f"{self.base_url}/databases/{self.database_id}", headers=self.headers)
            if response.status_code == 200:
                db_data = response.json()
                properties = db_data.get("properties", {})
                
                # Encontra a propriedade title
                for prop_name, prop_info in properties.items():
                    if prop_info.get("type") == "title":
                        self.title_property_name = prop_name
                        print(f"🔍 Propriedade title detectada: '{prop_name}'")
                        return prop_name
            
            # Fallback se não encontrar
            print("⚠️ Propriedade title não encontrada, usando 'Name' como fallback")
            self.title_property_name = "Name"
            return "Name"
            
        except Exception as e:
            print(f"❌ Erro ao detectar propriedade title: {e}")
            self.title_property_name = "Name"
            return "Name"
    
    def _parse_notion_response(self, response: Dict) -> List[Dict]:
        """Parse da resposta do Notion"""
        tasks = []
        for page in response.get('results', []):
            task = self._extract_task_data(page)
            if task:
                tasks.append(task)
        return tasks
    
    def _extract_task_data(self, page: Dict) -> Optional[Dict]:
        """Extrai dados da tarefa do formato Notion"""
        try:
            properties = page['properties']
            return {
                'id': page['id'],
                'title': self._extract_title(properties),
                'category': self._extract_select(properties, 'Category'),
                'priority': self._extract_select(properties, 'Priority'),
                'status': self._extract_select(properties, 'Status'),
                'estimated_time': self._extract_number(properties, 'Estimated Time'),
                'actual_time': self._extract_number(properties, 'Actual Time'),
                'created_date': self._extract_date(properties, 'Created'),
                'due_date': self._extract_date(properties, 'Due Date'),
                'scheduled_time': self._extract_date(properties, 'Scheduled Time'),
                'description': self._extract_rich_text(properties, 'Description'),
                'tags': self._extract_multi_select(properties, 'Tags')
            }
        except Exception as e:
            print(f"❌ Erro ao extrair tarefa: {e}")
            return None
    
    def _extract_title(self, properties: Dict) -> str:
        """Extrai título da tarefa"""
        # Procura por qualquer propriedade do tipo title
        for prop_name, prop_info in properties.items():
            if prop_info.get('type') == 'title':
                try:
                    if prop_info.get('title') and len(prop_info['title']) > 0:
                        return prop_info['title'][0]['text']['content']
                except (KeyError, IndexError, TypeError):
                    continue
        return "Tarefa sem título"
    
    def _extract_select(self, properties: Dict, field: str) -> str:
        """Extrai campo de seleção"""
        if field in properties and properties[field]['select']:
            return properties[field]['select']['name']
        return ""
    
    def _extract_multi_select(self, properties: Dict, field: str) -> List[str]:
        """Extrai campo de múltipla seleção"""
        if field in properties and properties[field]['multi_select']:
            return [item['name'] for item in properties[field]['multi_select']]
        return []
    
    def _extract_number(self, properties: Dict, field: str) -> Optional[float]:
        """Extrai campo numérico"""
        if field in properties and properties[field]['number'] is not None:
            return properties[field]['number']
        return None
    
    def _extract_date(self, properties: Dict, field: str) -> Optional[str]:
        """Extrai campo de data"""
        try:
            if field in properties:
                date_field = properties[field]
                if date_field and date_field.get('date') and date_field['date'].get('start'):
                    return date_field['date']['start']
        except (KeyError, TypeError, AttributeError) as e:
            # Log do erro sem quebrar a extração
            print(f"⚠️ Erro ao extrair data do campo '{field}': {e}")
        return None
    
    def _extract_rich_text(self, properties: Dict, field: str) -> str:
        """Extrai texto rico"""
        if field in properties and properties[field]['rich_text']:
            return properties[field]['rich_text'][0]['text']['content']
        return ""
    
    def _build_task_properties(self, task_data: Dict, schedule_info: Dict) -> Dict:
        """Constrói propriedades para criação de tarefa"""
        # Detecta o nome correto da propriedade title
        title_prop = self._get_title_property_name()
        
        # Propriedades básicas que sempre incluímos
        properties = {
            title_prop: {"title": [{"text": {"content": task_data.get('title', 'Nova Tarefa')}}]},
        }
        
        # Obtém lista de propriedades que existem no database
        existing_properties = self._get_existing_properties()
        
        # Adiciona propriedades condicionalmente (apenas se existem)
        if "Category" in existing_properties:
            properties["Category"] = {"select": {"name": task_data.get('category', 'Other')}}
        
        if "Priority" in existing_properties:
            properties["Priority"] = {"select": {"name": task_data.get('priority', 'Média')}}
        
        if "Status" in existing_properties:
            properties["Status"] = {"select": {"name": "Pendente"}}
        
        if "Estimated Time" in existing_properties:
            properties["Estimated Time"] = {"number": task_data.get('estimated_time', 30)}
        
        if "Scheduled Time" in existing_properties:
            scheduled_time = schedule_info.get('scheduled_datetime', '')
            if scheduled_time:
                properties["Scheduled Time"] = {"date": {"start": scheduled_time}}
        
        if "Description" in existing_properties:
            description = task_data.get('description', '')
            if description:
                properties["Description"] = {"rich_text": [{"text": {"content": description}}]}
        
        if "Tags" in existing_properties:
            tags = task_data.get('tags', [])
            if tags:
                properties["Tags"] = {"multi_select": [{"name": tag} for tag in tags]}
        
        print(f"🔨 Criando tarefa com {len(properties)} propriedades válidas")
        return properties
    
    def _get_existing_properties(self) -> Dict:
        """Obtém propriedades existentes no database"""
        try:
            response = requests.get(f"{self.base_url}/databases/{self.database_id}", headers=self.headers)
            if response.status_code == 200:
                db_data = response.json()
                return db_data.get("properties", {})
        except Exception as e:
            print(f"⚠️ Erro ao obter propriedades: {e}")
        return {}
    
    def _build_update_properties(self, updates: Dict) -> Dict:
        """Constrói propriedades para atualização"""
        properties = {}
        
        if 'status' in updates:
            properties['Status'] = {"select": {"name": updates['status']}}
        
        if 'actual_time' in updates:
            properties['Actual Time'] = {"number": updates['actual_time']}
        
        if 'feedback_rating' in updates:
            properties['User Rating'] = {"number": updates['feedback_rating']}
        
        return properties
