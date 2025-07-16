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
        
        # Inicializar com fallbacks para tokens ausentes
        notion_token = config.get('notion_token') or ''
        database_id = config.get('database_id') or ''
        claude_key = config.get('claude_api_key') or ''
        
        self.notion = NotionClient(notion_token, database_id)
        self.claude = ClaudeClient(claude_key)
        self.analyzer = PatternAnalyzer()
        self.feedback = FeedbackProcessor()
        
        # Verificar configuração
        missing_configs = []
        if not notion_token:
            missing_configs.append("NOTION_TOKEN")
        if not database_id:
            missing_configs.append("DATABASE_ID")
        if not claude_key:
            missing_configs.append("CLAUDE_API_KEY")
        
        if missing_configs:
            print(f"🔧 Configuração: {len(missing_configs)} variável(is) ausente(s): {', '.join(missing_configs)}")
            print(f"📖 Modo: Demonstração (funcionalidade limitada)")
            print(f"💡 Para integração completa, configure: {', '.join(missing_configs)}")
        else:
            print(f"✅ Configuração: Todas as integrações configuradas")
        
        print(f"🤖 CHRONOS AI v{self.version} initialized - Session: {self.session_id}")
    
    def orchestrate_schedule(self, task_data: Dict) -> Dict:
        """Método principal que orquestra todo o processo de agendamento"""
        
        # 1. Coleta contexto atual
        context = self._gather_context()
        
        # 2. Analisa padrões do usuário
        user_patterns = self.analyzer.get_current_patterns()
        
        # 3. Gera sugestão inteligente
        try:
            if self.config.get('claude_api_key'):
                print(f"🤖 Claude: Gerando sugestão inteligente para '{task_data.get('title', 'Tarefa')}'")
                suggestion = self.claude.generate_schedule_suggestion(
                    task_data, user_patterns, context
                )
                if suggestion and isinstance(suggestion, dict) and suggestion.get('scheduled_datetime'):
                    print(f"🤖 Claude: ✅ Sugestão IA gerada com sucesso")
                else:
                    print(f"🤖 Claude: ❌ Falha na geração - usando fallback local")
                    suggestion = self._generate_fallback_suggestion(task_data)
            else:
                print(f"🤖 Fallback: Usando algoritmo local (Claude não configurado)")
                suggestion = self._generate_fallback_suggestion(task_data)
        except Exception as e:
            error_type = type(e).__name__
            print(f"🤖 Claude: ❌ Erro [{error_type}] - fallback ativado")
            suggestion = self._generate_fallback_suggestion(task_data)
        
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
        try:
            if self.config.get('notion_token'):
                existing_tasks = self.notion.get_today_tasks()
                print(f"📋 Notion: {len(existing_tasks)} tarefa(s) encontrada(s) para hoje")
            else:
                existing_tasks = []
                print(f"📋 Notion: Pulando busca (token não configurado)")
        except Exception as e:
            print(f"📋 Notion: Falha ao buscar tarefas - usando lista vazia")
            existing_tasks = []
        
        return {
            'current_time': datetime.now().isoformat(),
            'existing_tasks': existing_tasks,
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
    
    def _generate_fallback_suggestion(self, task_data: Dict) -> Dict:
        """Gera sugestão básica quando Claude não está disponível"""
        from datetime import timedelta
        import uuid
        
        print(f"⚙️ Fallback: Gerando sugestão local para '{task_data.get('title', 'Tarefa')}'")
        
        # Lógica simples baseada na categoria
        hour_offset = 1  # Default
        reasoning_detail = "baseado em horário padrão"
        
        if task_data.get('category') == 'Development':
            hour_offset = 1  # Manhã
            reasoning_detail = "Development funciona melhor pela manhã"
        elif task_data.get('category') == 'Meetings':
            hour_offset = 3  # Meio do dia
            reasoning_detail = "Meetings são ideais no meio do dia"
        elif task_data.get('priority') == 'Urgente':
            hour_offset = 0.5  # Muito em breve
            reasoning_detail = "prioridade urgente requer ação imediata"
        
        scheduled_time = datetime.now() + timedelta(hours=hour_offset)
        
        suggestion = {
            'task_id': f"task_{uuid.uuid4().hex[:8]}",
            'scheduled_datetime': scheduled_time.isoformat(),
            'confidence': 0.6,
            'reasoning': f"Algoritmo local: {reasoning_detail}. Agendado para {scheduled_time.strftime('%H:%M')}",
            'alternatives': [
                f"Alternativa 1: {(scheduled_time + timedelta(hours=1)).strftime('%H:%M')}",
                f"Alternativa 2: {(scheduled_time + timedelta(hours=2)).strftime('%H:%M')}"
            ]
        }
        
        print(f"⚙️ Fallback: ✅ Sugestão local gerada (confiança: {suggestion['confidence']})")
        return suggestion
