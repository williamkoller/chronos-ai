from datetime import datetime, timedelta
import requests
import json
import re
import os
import random
from typing import Dict, List, Optional

class AIClient:
    """Cliente IA - Modo Desenvolvimento Rápido (Mock GPT)"""
    
    def __init__(self):
        # Modo de desenvolvimento para velocidade
        self.dev_mode = os.getenv('AI_DEV_MODE', 'true').lower() == 'true'
        
        if self.dev_mode:
            print(f"🚀 IA Modo Dev: Respostas instantâneas simulando GPT")
        else:
            # Configuração OpenAI Local (LocalAI) para produção
            self.openai_base_url = os.getenv('OPENAI_BASE_URL', 'http://localhost:8080/v1')
            self.openai_headers = {
                "Authorization": "Bearer local-key-not-needed",
                "Content-Type": "application/json"
            }
            self.openai_url = f"{self.openai_base_url}/chat/completions"
            self.openai_model = "gpt-3.5-turbo"
            print(f"🏠 IA Produção: LocalAI em {self.openai_base_url}")
    
    def generate_schedule_suggestion(self, task_data: Dict, user_patterns: Dict, context: Dict) -> Dict:
        """Gera sugestão de agendamento"""
        if self.dev_mode:
            return self._generate_dev_suggestion(task_data)
        
        prompt = self._build_scheduling_prompt(task_data, user_patterns, context)
        response = self._call_openai_local(prompt)
        
        if response:
            parsed = self._parse_scheduling_response(response)
            if parsed:
                return parsed
        
        return self._generate_dev_suggestion(task_data)
    
    def generate_pattern_analysis(self, daily_tasks: List[Dict], user_patterns: Dict) -> Dict:
        """Analisa padrões"""
        if self.dev_mode:
            return self._generate_dev_patterns(daily_tasks)
        
        prompt = self._build_pattern_prompt(daily_tasks, user_patterns)
        response = self._call_openai_local(prompt)
        
        if response:
            return self._parse_pattern_response(response)
        
        return self._generate_dev_patterns(daily_tasks)
    
    def process_feedback(self, feedback_data: Dict, current_patterns: Dict) -> Dict:
        """Processa feedback"""
        if self.dev_mode:
            return self._generate_dev_feedback(feedback_data)
        
        prompt = self._build_feedback_prompt(feedback_data, current_patterns)
        response = self._call_openai_local(prompt)
        
        if response:
            return self._parse_feedback_response(response)
        
        return self._generate_dev_feedback(feedback_data)
    
    def optimize_daily_schedule(self, tasks: List[Dict], preferences: Dict) -> Dict:
        """Otimiza cronograma diário"""
        if self.dev_mode:
            return self._generate_dev_optimization(tasks)
        
        prompt = self._build_optimization_prompt(tasks, preferences)
        response = self._call_openai_local(prompt)
        
        if response:
            try:
                return json.loads(response)
            except:
                pass
        
        return self._generate_dev_optimization(tasks)
    
    # === MODO DESENVOLVIMENTO (RÁPIDO) ===
    
    def _generate_dev_suggestion(self, task_data: Dict) -> Dict:
        """Sugestão instantânea simulando GPT"""
        now = datetime.now()
        
        # Lógica inteligente baseada na categoria
        category_timing = {
            'Development': (9, 11),  # Manhã
            'Meetings': (14, 16),    # Tarde
            'Research': (10, 12),    # Manhã
            'Documentation': (15, 17), # Tarde
            'Planning': (8, 10),     # Início do dia
            'Review': (16, 18),      # Final do dia
        }
        
        category = task_data.get('category', 'Development')
        start_hour, end_hour = category_timing.get(category, (10, 14))
        
        # Ajusta com base na prioridade
        if task_data.get('priority') == 'Urgente':
            start_hour = max(9, start_hour - 2)
        elif task_data.get('priority') == 'Baixa':
            start_hour = min(16, start_hour + 3)
        
        # Calcula horário
        if now.hour < start_hour:
            scheduled = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        elif now.hour > end_hour:
            scheduled = now.replace(hour=start_hour, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            scheduled = now + timedelta(hours=1)
        
        # Gera reasoning inteligente
        reasons = [
            f"{category} funciona melhor entre {start_hour}h-{end_hour}h",
            f"Prioridade {task_data.get('priority', 'Média')} sugere este horário",
            f"Estimativa de {task_data.get('estimated_time', 60)} minutos considerada"
        ]
        
        confidence = random.uniform(0.75, 0.95)
        
        return {
            "scheduled_datetime": scheduled.isoformat(),
            "confidence_score": confidence,
            "reasoning": f"GPT-Dev: {'. '.join(reasons[:2])}. Agendado para {scheduled.strftime('%H:%M')}",
            "duration_minutes": task_data.get('estimated_time', 60),
            "alternatives": [
                f"Alternativa 1: {(scheduled + timedelta(hours=1)).strftime('%H:%M')}",
                f"Alternativa 2: {(scheduled + timedelta(hours=2)).strftime('%H:%M')}"
            ]
        }
    
    def _generate_dev_patterns(self, tasks: List[Dict]) -> Dict:
        """Padrões simulados"""
        return {
            "productivity_peak": f"{random.randint(9, 11)}:00",
            "preferred_categories": ["Development", "Research"],
            "avg_task_duration": random.randint(45, 90),
            "efficiency_score": random.uniform(0.7, 0.9),
            "total_tasks_analyzed": len(tasks)
        }
    
    def _generate_dev_feedback(self, feedback_data: Dict) -> Dict:
        """Feedback simulado"""
        return {
            "learning_applied": True,
            "confidence_adjustment": random.uniform(-0.1, 0.1),
            "pattern_updates": ["time_preference", "duration_estimation"],
            "feedback_processed": True
        }
    
    def _generate_dev_optimization(self, tasks: List[Dict]) -> Dict:
        """Otimização simulada"""
        return {
            "workload_analysis": {
                "total_tasks": len(tasks),
                "estimated_hours": sum(task.get('estimated_time', 60) for task in tasks) / 60,
                "status": "normal" if len(tasks) < 8 else "high"
            },
            "recommendations": [
                "📅 Agende tarefas complexas pela manhã (9h-12h)",
                "⏰ Mantenha pausas de 15min entre tarefas",
                "🎯 Priorize tarefas urgentes antes das 14h",
                "🔄 Revise o cronograma às 16h"
            ]
        }
    
    # === MODO PRODUÇÃO (LocalAI) ===
    
    def _call_openai_local(self, prompt: str, max_tokens: int = 1500) -> Optional[str]:
        """Chama LocalAI apenas no modo produção"""
        if self.dev_mode:
            return None
        
        import time
        start_time = time.time()
        
        payload = {
            "model": self.openai_model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "top_p": 0.8
        }
        
        try:
            response = requests.post(self.openai_url, headers=self.openai_headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                elapsed = time.time() - start_time
                print(f"🏠 LocalAI respondeu em {elapsed:.1f}s")
                return result['choices'][0]['message']['content']
            else:
                elapsed = time.time() - start_time
                print(f"❌ LocalAI erro {response.status_code} em {elapsed:.1f}s")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"🔌 LocalAI: Falha de conexão - usando modo dev")
            return None
        except requests.exceptions.Timeout:
            print(f"⏱️ LocalAI: Timeout - usando modo dev")
            return None
        except Exception as e:
            print(f"⚠️ LocalAI erro: {type(e).__name__}")
            return None
    
    def _build_scheduling_prompt(self, task_data: Dict, user_patterns: Dict, context: Dict) -> str:
        """Prompt simplificado para agendamento"""
        return f"""
Tarefa: {task_data.get('title', '')}
Categoria: {task_data.get('category', '')}
Duração: {task_data.get('estimated_time', 60)} min
Prioridade: {task_data.get('priority', 'Média')}

Responda JSON:
{{
  "scheduled_datetime": "2025-01-21T10:00:00",
  "confidence_score": 0.85,
  "reasoning": "Manhã ideal para desenvolvimento",
  "duration_minutes": 60
}}
"""
    
    def _build_pattern_prompt(self, tasks: List[Dict], patterns: Dict) -> str:
        return f"Analise {len(tasks)} tarefas e retorne padrões em JSON."
    
    def _build_feedback_prompt(self, feedback: Dict, patterns: Dict) -> str:
        return f"Processe feedback e retorne ajustes em JSON."
    
    def _build_optimization_prompt(self, tasks: List[Dict], preferences: Dict) -> str:
        return f"Otimize {len(tasks)} tarefas e retorne recomendações em JSON."
    
    def _parse_scheduling_response(self, response: str) -> Dict:
        """Parse da resposta"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {}
    
    def _parse_pattern_response(self, response: str) -> Dict:
        return {}
    
    def _parse_feedback_response(self, response: str) -> Dict:
        return {} 