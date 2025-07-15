import datetime
import requests
import json
import re
from typing import Dict, List, Optional

class ClaudeClient:
    """Cliente para integração com Claude API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-sonnet-20240229"
    
    def generate_schedule_suggestion(self, task_data: Dict, user_patterns: Dict, context: Dict) -> Dict:
        """Gera sugestão de agendamento usando Claude"""
        
        prompt = self._build_scheduling_prompt(task_data, user_patterns, context)
        
        response = self._call_claude(prompt, max_tokens=1500)
        
        if response:
            return self._parse_scheduling_response(response)
        
        return self._default_suggestion(task_data)
    
    def analyze_user_patterns(self, task_history: List[Dict]) -> Dict:
        """Analisa padrões do usuário com Claude"""
        
        prompt = self._build_pattern_analysis_prompt(task_history)
        
        response = self._call_claude(prompt, max_tokens=2000)
        
        if response:
            return self._parse_pattern_response(response)
        
        return {}
    
    def process_feedback(self, feedback_data: Dict) -> Dict:
        """Processa feedback do usuário para melhorar sugestões"""
        
        prompt = self._build_feedback_prompt(feedback_data)
        
        response = self._call_claude(prompt, max_tokens=1000)
        
        if response:
            return self._parse_feedback_response(response)
        
        return {}
    
    def optimize_daily_schedule(self, daily_tasks: List[Dict], user_patterns: Dict) -> Dict:
        """Otimiza cronograma de um dia"""
        
        prompt = self._build_optimization_prompt(daily_tasks, user_patterns)
        
        response = self._call_claude(prompt, max_tokens=1500)
        
        if response:
            return self._parse_optimization_response(response)
        
        return {}
    
    def _call_claude(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Chama a API do Claude"""
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                return response.json()['content'][0]['text']
            else:
                print(f"❌ Erro Claude API: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao chamar Claude: {e}")
            return None
    
    def _build_scheduling_prompt(self, task_data: Dict, user_patterns: Dict, context: Dict) -> str:
        """Constrói prompt para agendamento"""
        return f"""
        Você é o CHRONOS AI, um especialista em otimização de cronogramas pessoais.

        PERFIL DO USUÁRIO (PADRÕES APRENDIDOS):
        {json.dumps(user_patterns, indent=2, ensure_ascii=False)}

        CONTEXTO ATUAL:
        {json.dumps(context, indent=2, ensure_ascii=False)}

        TAREFA PARA AGENDAR:
        {json.dumps(task_data, indent=2, ensure_ascii=False)}

        Com base nos padrões históricos e contexto atual, sugira o melhor agendamento.

        Considere:
        - Padrões de energia e produtividade
        - Carga de trabalho atual
        - Tipo de tarefa vs horário ideal
        - Histórico de performance

        Retorne JSON estruturado:
        {{
            "scheduled_datetime": "2024-01-15T09:00:00",
            "confidence_score": 0.92,
            "reasoning": "Horário de pico de produtividade para desenvolvimento",
            "duration_minutes": 120,
            "alternatives": [
                {{"time": "14:00", "score": 0.78, "reason": "Segunda opção"}}
            ],
            "context_factors": ["high_energy_morning", "no_meetings_before"],
            "success_probability": 0.88
        }}
        """
    
    def _build_pattern_analysis_prompt(self, task_history: List[Dict]) -> str:
        """Constrói prompt para análise de padrões"""
        return f"""
        Analise o histórico de tarefas e identifique padrões de produtividade:

        HISTÓRICO DE TAREFAS:
        {json.dumps(task_history[-50:], indent=2, ensure_ascii=False)}

        Identifique:
        1. Horários de maior produtividade por tipo de tarefa
        2. Padrões de energia durante a semana
        3. Fatores que afetam performance
        4. Preferências implícitas do usuário
        5. Correlações entre contexto e produtividade

        Retorne JSON com padrões identificados:
        {{
            "energy_patterns": {{
                "peak_hours": ["09:00-11:00", "14:00-16:00"],
                "low_energy": ["13:00-14:00", "16:00-17:00"]
            }},
            "task_preferences": {{
                "development": {{"best_hours": ["09:00-12:00"], "efficiency": 0.92}},
                "meetings": {{"best_hours": ["14:00-17:00"], "efficiency": 0.85}}
            }},
            "behavioral_patterns": {{
                "planning_style": "prefers_morning_blocks",
                "break_needs": "15min_between_tasks",
                "focus_duration": "90_minutes_max"
            }},
            "productivity_factors": {{
                "day_of_week_impact": {{"monday": 1.1, "friday": 0.8}},
                "time_estimation_accuracy": 0.75
            }}
        }}
        """
    
    def _build_feedback_prompt(self, feedback_data: Dict) -> str:
        """Constrói prompt para processar feedback"""
        return f"""
        Analise este feedback do usuário para melhorar futuras sugestões:

        FEEDBACK RECEBIDO:
        {json.dumps(feedback_data, indent=2, ensure_ascii=False)}

        Extraia insights sobre:
        1. O que funcionou bem
        2. O que precisa ser ajustado
        3. Padrões nas preferências
        4. Ajustes necessários no modelo

        Retorne insights estruturados:
        {{
            "insights": {{
                "preference_adjustment": "usuário prefere manhãs para código",
                "timing_correction": "sugestões 30min mais cedo",
                "pattern_validation": "confirma produtividade matinal"
            }},
            "adjustments": {{
                "confidence_modifier": 0.1,
                "time_preference_shift": "-30min",
                "category_weight_change": {{"development": 1.2}}
            }},
            "learning_priority": "high"
        }}
        """
    
    def _build_optimization_prompt(self, daily_tasks: List[Dict], user_patterns: Dict) -> str:
        """Constrói prompt para otimização diária"""
        return f"""
        Otimize o cronograma do dia considerando todas as tarefas:

        TAREFAS DO DIA:
        {json.dumps(daily_tasks, indent=2, ensure_ascii=False)}

        PADRÕES DO USUÁRIO:
        {json.dumps(user_patterns, indent=2, ensure_ascii=False)}

        Analise e otimize:
        1. Sequência ideal das tarefas
        2. Identificação de conflitos
        3. Oportunidades de agrupamento
        4. Necessidades de pausas
        5. Carga de trabalho total

        Retorne otimização:
        {{
            "optimized_sequence": [
                {{"task_id": "123", "start_time": "09:00", "reasoning": "alta energia"}}
            ],
            "conflicts_detected": ["overlapping meetings"],
            "workload_analysis": {{
                "total_hours": 7.5,
                "intensity_level": "high",
                "sustainability_score": 0.75
            }},
            "recommendations": ["add 15min breaks", "move creative work to morning"]
        }}
        """
    
    def _parse_scheduling_response(self, response: str) -> Dict:
        """Parse da resposta de agendamento"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"❌ Erro ao parsear resposta de agendamento: {e}")
        
        return self._default_suggestion({})
    
    def _parse_pattern_response(self, response: str) -> Dict:
        """Parse da resposta de análise de padrões"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"❌ Erro ao parsear padrões: {e}")
        
        return {}
    
    def _parse_feedback_response(self, response: str) -> Dict:
        """Parse da resposta de feedback"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"❌ Erro ao parsear feedback: {e}")
        
        return {}
    
    def _parse_optimization_response(self, response: str) -> Dict:
        """Parse da resposta de otimização"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"❌ Erro ao parsear otimização: {e}")
        
        return {}
    
    def _default_suggestion(self, task_data: Dict) -> Dict:
        """Sugestão padrão em caso de erro"""
        return {
            "scheduled_datetime": (datetime.now() + datetime.timedelta(hours=1)).isoformat(),
            "confidence_score": 0.3,
            "reasoning": "Sugestão padrão - dados insuficientes",
            "duration_minutes": task_data.get('estimated_time', 60),
            "alternatives": [],
            "context_factors": [],
            "success_probability": 0.5
        }
