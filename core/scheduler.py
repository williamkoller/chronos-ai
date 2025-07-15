from datetime import datetime
from typing import Dict

class ChronosCore:
    """Motor principal do CHRONOS AI - Orquestra todo o sistema"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.version = "1.0.0"
        self.session_id = self._generate_session_id()
        
        # Inicializa componentes
        from integrations.notion_client import NotionClient
        from integrations.claude_client import ClaudeClient
        from learning.pattern_analyzer import PatternAnalyzer
        from learning.feedback_processor import FeedbackProcessor
        
        self.notion = NotionClient(config['notion_token'], config['database_id'])
        self.claude = ClaudeClient(config['claude_api_key'])
        self.analyzer = PatternAnalyzer()
        self.feedback = FeedbackProcessor()
        
        print(f"🤖 CHRONOS AI v{self.version} initialized - Session: {self.session_id}")
    
    def orchestrate_schedule(self, task_data: Dict) -> Dict:
        """Método principal que orquestra todo o processo de agendamento"""
        
        # 1. Coleta contexto atual
        context = self._gather_context()
        
        # 2. Analisa padrões do usuário
        user_patterns = self.analyzer.get_current_patterns()
        
        # 3. Gera sugestão inteligente
        suggestion = self.claude.generate_schedule_suggestion(
            task_data, user_patterns, context
        )
        
        # 4. Valida e otimiza
        optimized_suggestion = self._optimize_suggestion(suggestion, context)
        
        # 5. Prepara resposta
        return {
            'session_id': self.session_id,
            'task': task_data,
            'suggestion': optimized_suggestion,
            'context': context,
            'confidence': optimized_suggestion.get('confidence', 0.5),
            'reasoning': optimized_suggestion.get('reasoning', ''),
            'alternatives': optimized_suggestion.get('alternatives', [])
        }
    
    def _gather_context(self) -> Dict:
        """Coleta contexto atual do usuário"""
        return {
            'current_time': datetime.now().isoformat(),
            'existing_tasks': self.notion.get_today_tasks(),
            'recent_performance': self.analyzer.get_recent_performance(),
            'energy_patterns': self.analyzer.get_energy_patterns(),
            'workload_status': self._calculate_workload_status()
        }
    
    def _optimize_suggestion(self, suggestion: Dict, context: Dict) -> Dict:
        """Otimiza sugestão baseada no contexto"""
        # Implementa lógica de otimização
        return suggestion
    
    def _calculate_workload_status(self) -> Dict:
        """Calcula status atual da carga de trabalho"""
        return {'status': 'normal', 'capacity': 0.7}
    
    def _generate_session_id(self) -> str:
        """Gera ID único da sessão"""
        import uuid
        return f"chronos_{uuid.uuid4().hex[:8]}"
