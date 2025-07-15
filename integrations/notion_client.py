import datetime
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
    
    def get_tasks(self, days_back: int = 30) -> List[Dict]:
        """Busca tarefas do Notion"""
        url = f"{self.base_url}/databases/{self.database_id}/query"
        
        filter_payload = {
            "filter": {
                "property": "Created",
                "date": {
                    "after": (datetime.now() - datetime.timedelta(days=days_back)).isoformat()
                }
            },
            "sorts": [{"property": "Created", "direction": "descending"}]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=filter_payload)
            if response.status_code == 200:
                return self._parse_notion_response(response.json())
            else:
                print(f"❌ Erro Notion API: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Erro na conexão Notion: {e}")
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
        if 'Name' in properties and properties['Name']['title']:
            return properties['Name']['title'][0]['text']['content']
        return ""
    
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
        if field in properties and properties[field]['date']:
            return properties[field]['date']['start']
        return None
    
    def _extract_rich_text(self, properties: Dict, field: str) -> str:
        """Extrai texto rico"""
        if field in properties and properties[field]['rich_text']:
            return properties[field]['rich_text'][0]['text']['content']
        return ""
    
    def _build_task_properties(self, task_data: Dict, schedule_info: Dict) -> Dict:
        """Constrói propriedades para criação de tarefa"""
        return {
            "Name": {"title": [{"text": {"content": task_data.get('title', 'Nova Tarefa')}}]},
            "Category": {"select": {"name": task_data.get('category', 'Geral')}},
            "Priority": {"select": {"name": task_data.get('priority', 'Média')}},
            "Status": {"select": {"name": "Agendado IA"}},
            "Estimated Time": {"number": task_data.get('estimated_time', 30)},
            "Scheduled Time": {"date": {"start": schedule_info.get('scheduled_datetime', '')}},
            "Description": {"rich_text": [{"text": {"content": task_data.get('description', '')}}]},
            "AI Confidence": {"number": schedule_info.get('confidence_score', 0.5)},
            "AI Reasoning": {"rich_text": [{"text": {"content": schedule_info.get('reasoning', '')}}]}
        }
    
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
